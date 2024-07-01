from pathlib import Path
from typing import List
from ..domain.Video import Video
from datetime import datetime, timezone


class VideosRepository:
    """Provides persistance for video instances"""

    def __init__(self, data_file: Path):
        self.data_file = data_file
    
    def get_videos(self) -> List[Video]:
        return [
            Video(
                id="2134",
                title="Lorem ipsum",
                created_at=datetime.now(timezone.utc)
            )
        ]
