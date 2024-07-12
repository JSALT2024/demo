from .VideoFolderRepository import VideoFolderRepository
from pathlib import Path


class VideoFolderRepositoryFactory:
    """
    Creates light, disposable instances of VideoFolderRepository class
    for the video ID you provide
    """
    def __init__(self, videos_data_folder: Path):
        self.videos_data_folder = videos_data_folder
        videos_data_folder.mkdir(parents=True, exist_ok=True)

    def get_repository(self, video_id: str) -> VideoFolderRepository:
        # The idea is that should the videos be moved to some external
        # object storage, this method can be modified to handle their
        # downloading or creation of other video repositories.
        return VideoFolderRepository(
            video_id=video_id,
            video_folder=self.videos_data_folder / video_id
        )
