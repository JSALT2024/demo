from pathlib import Path
from typing import List, Dict, Optional
from ..domain.Video import Video
import pickle


class VideosRepository:
    """Provides persistance for video instances"""

    def __init__(self, data_file: Path):
        self.data_file = data_file

        self._videos: Dict[str, Video] = {}
        
        self._load_data()
    
    def _load_data(self):
        if not self.data_file.is_file():
            return
        
        with open(self.data_file, "rb") as file:
            self._videos = pickle.load(file)

    def _write_data(self):
        with open(self.data_file, "wb") as file:
            pickle.dump(self._videos, file)
    
    def all(self) -> List[Video]:
        return list(self._videos.values())
    
    def store(self, video: Video):
        self._videos[video.id] = video
        self._write_data()
    
    def remove(self, video_id: str):
        del self._videos[video_id]
        self._write_data()
    
    def load(self, id: str) -> Optional[Video]:
        if id not in self._videos:
            return None
        v = self._videos[id]
        assert v.id == id
        return v
