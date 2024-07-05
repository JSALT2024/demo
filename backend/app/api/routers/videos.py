from fastapi import APIRouter, HTTPException, UploadFile, HTTPException, \
    File, Form
from fastapi.responses import StreamingResponse, FileResponse
from typing import List, Annotated
import os
import aiofiles
from ..models.VideoOut import VideoOut
from ...domain.Video import Video
from ..application import ApplicationDependency
from dataclasses import asdict
from datetime import datetime, timezone
import uuid
import logging


router = APIRouter()


@router.get("")
def list_videos(app: ApplicationDependency) -> List[VideoOut]:
    # fetch videos from the storage
    videos: List[Video] = app.videos_repository.all()

    # convert videos to the output model type
    return [VideoOut(**asdict(video)) for video in videos]


@router.get("/{video_id}")
def get_video(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = app.videos_repository.load(video_id)
    if video is None:
        raise HTTPException(
            status_code=404,
            detail="There is no video with the given ID"
        )
    return VideoOut(**asdict(video))


@router.get("/{video_id}/video-file")
def get_video_file(video_id: str, app: ApplicationDependency) -> VideoOut:
    video = app.videos_repository.load(video_id)
    if video is None:
        raise HTTPException(
            status_code=404,
            detail="There is no video with the given ID"
        )
    files_repo = app.video_files_repository_factory.get_repository(video_id)
    return FileResponse(files_repo.video_file_path, media_type=video.media_type)


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

    # === create the video record ===
    
    video = Video(
        id=str(uuid.uuid4()),
        title=file.filename,
        media_type=media_type,
        created_at=datetime.now(timezone.utc)
    )
    app.videos_repository.store(video)

    # === upload the video file into the storage ===

    CHUNK_SIZE = 1024 * 1024  # 1MB
    files_repo = app.video_files_repository_factory.get_repository(video.id)

    try:
        files_repo.video_file_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(files_repo.video_file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logging.exception(e)
        raise HTTPException(
            status_code=500, 
            detail="There was an error uploading the file"
        )
    finally:
        await file.close()

    # === trigger processing of the video ===

    # TODO: trigger procesing

    return {"message": f"Successfuly uploaded {file.filename}"}