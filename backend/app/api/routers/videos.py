from fastapi import APIRouter, HTTPException, UploadFile, HTTPException, \
    File, Form
from fastapi.responses import FileResponse
from typing import List, Annotated
import aiofiles
from ..models.VideoOut import VideoOut
from ...domain.Video import Video
from ...domain.VideoFile import VideoFile
from ..application import ApplicationDependency
from datetime import datetime, timezone
import uuid
import logging
import mimetypes
from pathlib import Path
from ...services.process_video import process_video
import threading
import glob
import base64


router = APIRouter()


def get_video_or_fail(video_id: str, app: ApplicationDependency) -> Video:
    """Fetches a video from the repository or throws a 404 error"""
    video = app.videos_repository.load(video_id)
    if video is None:
        raise HTTPException(
            status_code=404,
            detail="There is no video with the given ID"
        )
    return video


@router.get("")
def list_videos(app: ApplicationDependency) -> List[VideoOut]:
    # fetch videos from the storage
    videos: List[Video] = app.videos_repository.all()

    # convert videos to the output model type
    return [VideoOut.from_model(video) for video in videos]


@router.get("/{video_id}")
def get_video(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = get_video_or_fail(video_id, app)
    return VideoOut.from_model(video)


@router.get("/{video_id}/uploaded-file")
def get_uploaded_file(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = get_video_or_fail(video_id, app)
    if video.uploaded_file is None:
        raise HTTPException(
            status_code=404,
            detail="The video file has not finished uploading yet."
        )
    
    folder_repo = app.video_folder_repository_factory.get_repository(video_id)
    return FileResponse(
        folder_repo.to_global_path(video.uploaded_file.file_path),
        media_type=video.uploaded_file.media_type
    )


@router.get("/{video_id}/normalized-file")
def get_normalized_file(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = get_video_or_fail(video_id, app)
    if video.normalized_file is None:
        raise HTTPException(
            status_code=404,
            detail="The video has not been normalized yet."
        )
    
    folder_repo = app.video_folder_repository_factory.get_repository(video_id)
    normalized_file_path = folder_repo.to_global_path(
        video.normalized_file.file_path
    )
    if not normalized_file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="The normalized video file is missing"
        )
    return FileResponse(
        normalized_file_path,
        media_type=video.normalized_file.media_type
    )


@router.get("/{video_id}/geometry")
def get_geometry(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = get_video_or_fail(video_id, app)
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    file_path = folder_repo.to_global_path("geometry.json")
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="The video geometry has not been extracted yet."
        )
    return FileResponse(file_path, media_type="application/json")


@router.get("/{video_id}/cropped/{crop_name}")
def get_crops(video_id: str, crop_name: str, app: ApplicationDependency):
    if crop_name not in ["left_hand", "right_hand", "face", "images"]:
        raise HTTPException(status_code=404, detail="Unknown crop name.")
    video = get_video_or_fail(video_id, app)
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    folder_path = folder_repo.to_global_path("cropped_" + crop_name)
    if not folder_path.is_dir():
        raise HTTPException(
            status_code=404,
            detail="Request crops have not been extracted yet."
        )
    
    # build up the JSON response (because I couldn't get BSON to work)
    frame_files = sorted(glob.glob(
        pathname="frame_*.jpg",
        root_dir=folder_path
    ))
    return [
        base64.b64encode(Path(folder_path, file).read_bytes())
        for file in frame_files
    ]


@router.get("/{video_id}/clips-collection")
def get_geometry(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = get_video_or_fail(video_id, app)
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    file_path = folder_repo.to_global_path("clips_collection.json")
    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Clips collection file has not been extracted yet."
        )
    return FileResponse(file_path, media_type="application/json")


@router.post("", status_code=201)
async def upload_new_video(
    media_type: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    app: ApplicationDependency
):
    """
    Uploads a new video. Code based on:
    https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
    """

    # validate the media type
    if mimetypes.guess_extension(media_type) is None:
        raise HTTPException(
            status_code=422,
            detail=f"The provided media type '{media_type}' is not known.",
        )
    
    # === create the video record ===
    
    video = Video(
        id=str(uuid.uuid4()),
        title=file.filename,
        created_at=datetime.now(timezone.utc),
        uploaded_file=None,
        normalized_file=None
    )
    app.videos_repository.store(video)

    # === upload the video file into the storage ===

    CHUNK_SIZE = 1024 * 1024  # 1MB
    
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)

    file_extension: str = mimetypes.guess_extension(media_type)
    file_path: Path = folder_repo.to_global_path(
        Path("uploaded_file").with_suffix(file_extension)
    )
    file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500,
            detail="There was an error uploading the file, see the server log."
        )
    finally:
        await file.close()

    # === extract file metadata ===

    video.uploaded_file = VideoFile.from_existing_file(
        folder_repo.root_path,
        file_path
    )
    app.videos_repository.store(video)

    # === trigger processing of the video ===

    # TODO: run this in a proper background job instead of this clunky
    # threading code that does not care about server termination
    def run_processing():
        print("Processing video...")
        process_video(video, app.videos_repository, folder_repo)
        print("Processing done.")
    
    thread = threading.Thread(target=run_processing)
    thread.start()

    return {"message": f"Successfuly uploaded {file.filename}"}

@router.post("/{video_id}/reprocess", status_code=202)
async def reprocess_video(video_id: str, app: ApplicationDependency):
    video = get_video_or_fail(video_id, app)
    folder_repo = app.video_folder_repository_factory.get_repository(video_id)

    # === trigger processing of the video ===

    # TODO: run this in a proper background job instead of this clunky
    # threading code that does not care about server termination
    def run_processing():
        print("Processing video...")
        process_video(video, app.videos_repository, folder_repo)
        print("Processing done.")
    
    thread = threading.Thread(target=run_processing)
    thread.start()

    return {"message": "Re-processing started."}
