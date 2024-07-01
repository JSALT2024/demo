from .services.VideosRepository import VideosRepository
from .services.VideoFilesRepositoryFactory import VideoFielsRepositoryFactory
from pathlib import Path

class Application:
    """
    Encapsulates all the global services used in the application. This class
    instance is enough to use the backend's logic without the HTTP server layer.
    It acts as the single point where these services are instantiated and linked
    together.
    """
    def __init__(
        self,
        storage_folder: Path
    ):
        storage_folder.mkdir(parents=True, exist_ok=True)
        
        self.videos_repository = VideosRepository(
            data_file=storage_folder / "videos.json"
        )
        self.video_files_repository_factory = VideoFielsRepositoryFactory(
            videos_data_folder=storage_folder / "videos_data"
        )
