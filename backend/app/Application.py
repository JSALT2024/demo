from .services.VideosRepository import VideosRepository
from .services.VideoFolderRepositoryFactory import VideoFolderRepositoryFactory
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

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
            data_file=storage_folder / "videos.pkl"
        )
        self.video_folder_repository_factory = VideoFolderRepositoryFactory(
            videos_data_folder=storage_folder / "videos_data"
        )

        self.executor = ThreadPoolExecutor(
            max_workers=1
        )
        "Runs CPU-intensive tasks, such as video processing and LLM execution"
