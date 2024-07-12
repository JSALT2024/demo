from pathlib import Path
from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from ..domain.VideoFile import VideoFile
from ..preprocessing.VideoNormalizer import VideoNormalizer
from pathlib import Path
import cv2


def process_video(
    video: Video,
    videos_repository: VideosRepository,
    folder_repo: VideoFolderRepository
):
    """
    Runs all of the processing after the video is uploaded, including
    preprocessing, encoders, and autoregressive llama translation.
    """

    # === normalize video ===

    normalized_file_path = folder_repo.to_global_path(
        Path("normalized-file").with_suffix(
            video.uploaded_file.file_path.suffix
        )
    )
    normalizer = VideoNormalizer(
        input_video_path=str(
            folder_repo.to_global_path(video.uploaded_file.file_path)
        ),
        output_video_path=str(normalized_file_path),
        target_fps=24
    )
    normalizer.process_video()
    normalizer.close_output()

    video.normalized_file = VideoFile.from_existing_file(
        folder_repo.root_path,
        normalized_file_path
    )

    # === store progress ===

    videos_repository.store(video)


# DEBUGGING
if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    folder_repo = app.video_folder_repository_factory.get_repository(video.id)
    process_video(video, app.videos_repository, folder_repo)
