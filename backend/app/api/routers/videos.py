from fastapi import APIRouter, HTTPException, UploadFile, HTTPException
from typing import List
import os
import aiofiles
from ..models.VideoOut import VideoOut
from ...domain.Video import Video
from ..application import ApplicationDependency
from dataclasses import asdict


router = APIRouter()


@router.get("")
def list_videos(app: ApplicationDependency) -> List[VideoOut]:
    # fetch videos from the storage
    videos: List[Video] = app.videos_repository.get_videos()

    # convert videos to the output model type
    return [VideoOut(**asdict(video)) for video in videos]


@router.post("")
async def upload_new_video(file: UploadFile):
    """
    Uploads a new video. Code based on:
    https://stackoverflow.com/questions/73442335/how-to-upload-a-large-file-%E2%89%A53gb-to-fastapi-backend
    """

    # TODO: connect this with the storage layer,
    # create new video model when a video is uploaded,
    # store the video file in the storage
    # trigger video preprocessing logic, splitting it into frames and stuff

    CHUNK_SIZE = 1024 * 1024  # 1MB
    try:
        filepath = os.path.join("storage", os.path.basename(file.filename))
        async with aiofiles.open(filepath, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)
    except Exception:
        raise HTTPException(
            status_code=500, 
            detail="There was an error uploading the file"
        )
    finally:
        await file.close()

    return {"message": f"Successfuly uploaded {file.filename}"}