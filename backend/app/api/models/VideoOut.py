from pydantic import BaseModel
from datetime import datetime
from ...domain.Video import Video
from ...domain.VideoFile import VideoFile
from typing import Optional


class VideoFileOut(BaseModel):
    media_type: str
    duration_seconds: float
    frame_count: int
    framerate: float
    frame_width: int
    frame_height: int
    file_size_bytes: int

    @staticmethod
    def from_model(model: Optional[VideoFile]) -> Optional["VideoFileOut"]:
        if model is None:
            return None
        return VideoFileOut(
            media_type=model.media_type,
            duration_seconds=model.duration_seconds,
            frame_count=model.frame_count,
            framerate=model.framerate,
            frame_width=model.frame_width,
            frame_height=model.frame_height,
            file_size_bytes=model.file_size_bytes
        )


class VideoOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    uploaded_file: Optional[VideoFileOut]
    normalized_file: Optional[VideoFileOut]

    @staticmethod
    def from_model(model: Video):
        return VideoOut(
            id=model.id,
            title=model.title,
            created_at=model.created_at,
            uploaded_file=VideoFileOut.from_model(model.uploaded_file),
            normalized_file=VideoFileOut.from_model(model.normalized_file)
        )
