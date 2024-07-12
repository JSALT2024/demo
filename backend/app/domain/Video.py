from dataclasses import dataclass
from datetime import datetime
from .VideoFile import VideoFile
from typing import Optional


@dataclass
class Video:
    """
    Represents one uploaded/recorded video that is being analyzed
    and translated. It represents the uploaded video file, as well as its
    normalized variant, all clips it has been split up into and the outputs
    from the translation model, as well as the encoders and preprocessing.
    """

    id: str
    "Identifier of the video"

    title: str
    "Human-readable title of the video"

    created_at: datetime
    "When was the video upload initiated"

    uploaded_file: Optional[VideoFile]
    """
    Metadata about the raw uploaded file stored in the video storage folder.
    Is None as long as the file is being uploaded.
    """

    normalized_file: Optional[VideoFile]
    """
    Metadata about the normalized file stored in the video storage folder.
    Is None as long as the uploaded file is being normalized.
    """
