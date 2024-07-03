from pathlib import Path
from typing import List, Dict, Optional
from ..domain.Video import Video
from datetime import datetime, timezone
import json
from dataclasses import asdict


class VideosRepository:
    """Provides persistance for video instances"""

    def __init__(self, data_file: Path):
        self.data_file = data_file

        self._videos: Dict[str, Video] = {}
        
        self._load_data()
    
    def _load_data(self):
        if not self.data_file.is_file():
            return
        
        with open(self.data_file, "r") as file:
            data: dict = json.load(file)
        
        self._videos = {
            id: Video(**v)
            for id, v in data.items()
        }

    def _write_data(self):
        data = {
            video.id: asdict(video)
            for video in self._videos.values()
        }

        with open(self.data_file, "w") as file:
            json.dump(data, file)
    
    def all(self) -> List[Video]:
        return list(self._videos.values())
    
    def store(self, video: Video):
        self._videos[video.id] = video
    
    def load(self, id: str) -> Optional[Video]:
        if id not in self._videos:
            return None
        v = self._videos[id]
        assert v.id == id
        return v
