from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from .VideoProcessor import VideoProcessor
from ..translation.SignLlavaCache import SignLlavaCache
import os


def process_video(
    video: Video,
    videos_repository: VideosRepository,
    folder_repo: VideoFolderRepository,
    sign_llava_cache: SignLlavaCache
):
    """
    Runs all of the processing after the video is uploaded, including
    preprocessing, encoders, and autoregressive llama translation.
    """
    
    print("STARTING VIDEO PROCESSING")
    print("-------------------------")
    
    processor = VideoProcessor(
        video=video,
        videos_repository=videos_repository,
        video_folder=folder_repo,
        sign_llava_cache=sign_llava_cache,
        huggingface_token=os.environ.get("HF_TOKEN")
    )
    processor.run()
    
    print("=====================")
    print("VIDEO PROCESSING DONE")


# DEBUGGING
if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    process_video(
        video,
        app.videos_repository,
        folder_repo,
        app.sign_llava_cache
    )
