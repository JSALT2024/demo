from pathlib import Path


class VideoFolderRepository:
    """
    Encapsulates access to files that describe a single uploaded video
    (the video itself, its frames, metadata and translation results)
    This repository assumes the video is stored in the local file system
    in a single folder.
    """
    def __init__(self, video_id: str, video_folder: Path):
        self.video_id = video_id
        self._video_folder = video_folder

    def to_global_path(self, repository_local_path: Path) -> Path:
        """Converts repo-local path to an actual, usable path"""
        return self._video_folder / repository_local_path
    
    @property
    def root_path(self) -> Path:
        """Path to the folder representing this video repository"""
        return self._video_folder
