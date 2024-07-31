from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from .VideoProcessor import VideoProcessor
from ..translation.SignLlavaCache import SignLlavaCache
import os
import logging
import time


def process_video(
    video: Video,
    videos_repository: VideosRepository,
    video_folder: VideoFolderRepository,
    sign_llava_cache: SignLlavaCache,
    force_all=False
):
    """
    Runs all of the processing after the video is uploaded, including
    preprocessing, encoders, and autoregressive llama translation.
    """

    # prepare the processing logger
    logger: logging.Logger = logging.getLogger(__name__)
    video_folder.LOG_FILE.unlink(missing_ok=True)
    file_handler = logging.FileHandler(
        video_folder.LOG_FILE,
        mode="a",
        encoding="utf-8"
    )
    formatter = logging.Formatter(
        "[{asctime}] {levelname} {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # mark the video as being processed
    video.is_processing = True
    videos_repository.store(video)
    
    # start video processing
    logger.info("STARTING VIDEO PROCESSING")
    logger.info("-------------------------")
    
    try:
        processor = VideoProcessor(
            video=video,
            videos_repository=videos_repository,
            video_folder=video_folder,
            sign_llava_cache=sign_llava_cache,
            huggingface_token=os.environ.get("HF_TOKEN"),
            logger=logger
        )
        processor.run(force_all=force_all)
    except:
        logger.exception("Uncaught exception during video processing:")
        raise
    
    logger.info("=====================")
    logger.info("VIDEO PROCESSING DONE")

    # wait 2 seconds so that the log gets sent to frontend and then
    # terminate the log watching script
    time.sleep(2.0)

    # mark the video as done
    video.is_processing = False
    videos_repository.store(video)


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
