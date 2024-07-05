from dataclasses import dataclass
from datetime import datetime


@dataclass
class Video:
    """
    Represents one uploaded/recorded video that is being analyzed
    and translated.
    """

    id: str
    "Identifier of the video"

    title: str
    "Human-readable title of the video"

    media_type: str
    "MIME type of the video"

    created_at: datetime
    "When was the video uploaded"
