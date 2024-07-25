from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from .VideoProcessor import VideoProcessor
import os


def process_video(
    video: Video,
    videos_repository: VideosRepository,
    folder_repo: VideoFolderRepository
):
    """
    Runs all of the processing after the video is uploaded, including
    preprocessing, encoders, and autoregressive llama translation.
    """
    processor = VideoProcessor(
        video=video,
        videos_repository=videos_repository,
        folder_repo=folder_repo,
        huggingface_token=os.environ.get("HUGGINGFACE_TOKEN")
    )
    processor.run()


# DEBUGGING
if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    process_video(video, app.videos_repository, folder_repo)
