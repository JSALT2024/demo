from pathlib import Path


class VideoFilesRepository:
    """
    Encapsulates access to files that describe a single uploaded video
    (the video itself, its frames, metadata and translation results)
    This repository assumes the video is stored in the local file system
    in a single folder.
    """
    def __init__(self, video_id: str, video_folder: Path):
        self.video_id = video_id
        self._video_folder = video_folder
    
    @property
    def video_file_path(self) -> Path:
        return self._video_folder / "video-file" # extension is unknown
