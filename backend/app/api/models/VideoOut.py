from pydantic import BaseModel
from datetime import datetime


class VideoOut(BaseModel):
    id: str
    title: str
    created_at: datetime
