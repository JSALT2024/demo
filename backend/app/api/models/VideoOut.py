from pydantic import BaseModel
from datetime import datetime


class VideoOut(BaseModel):
    id: str
    title: str
    media_type: str
    created_at: datetime
