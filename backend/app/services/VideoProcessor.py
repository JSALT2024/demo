from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from ..domain.VideoFile import VideoFile
from ..preprocessing.VideoNormalizer import VideoNormalizer
from ..preprocessing.FrameEnumerator import FrameEnumerator
from ..preprocessing.MediapipeProcessor import MediapipeProcessor
from pathlib import Path
import shutil
from typing import Union


class VideoProcessor:
    """
    Performs all the video processing tasks after a video is uploaded to the
    server, including its translation by the LLM.
    """

    def __init__(
        self,
        video: Video,
        videos_repository: VideosRepository,
        folder_repo: VideoFolderRepository
    ):
        self.video = video
        self.videos_repository = videos_repository
        self.folder_repo = folder_repo

        # check upload finished
        if video.uploaded_file is None:
            raise Exception(
                "Only a video that has already finished " +
                "uploading can be processed."
            )

        # define common file paths
        self.UPLOADED_FILE = self.path(video.uploaded_file.file_path)
        self.NORMALIZED_FILE = self.path("normalized_file.mp4") # always mp4
        self.GEOMETRY_FILE = self.path("geometry.json")
        self.CROPPED_LEFT_HAND_FOLDER = self.path("cropped_left_hand")
        self.CROPPED_RIGHT_HAND_FOLDER = self.path("cropped_right_hand")
        self.CROPPED_FACE_FOLDER = self.path("cropped_face")
    
    def path(self, relative_path: Union[str, Path]) -> Path:
        """Returns the global path of a file inside the storage video folder"""
        return self.folder_repo.to_global_path(Path(relative_path))

    def run(self, force_all=False):
        """
        Runs all of the processing tasks. The force_all forces even
        the execution of phases that have already been executed before.
        """
        
        # initial preprocessing
        if not self.NORMALIZED_FILE.exists() and not force_all:
            self.normalize_uploaded_file()
            self.enumerate_normalized_file()

        # mediapipe
        self.run_mediapipe()

        # encoders

        # LLaVA

    def normalize_uploaded_file(self):
        normalizer = VideoNormalizer(
            input_video_path=str(self.UPLOADED_FILE),
            output_video_path=str(self.NORMALIZED_FILE),
            fps_lower_bound=23, # because many videos are 23.98 FPS
            fps_higher_bound=30 # because many videos are 30 FPS
        )
        normalizer.process_video()
        normalizer.close_output()

        self.extract_normalized_file_metadata()

    def enumerate_normalized_file(self):
        temp_file = self.NORMALIZED_FILE.with_stem("temp_enumerated_file")

        video_loader = FrameEnumerator(
            input_video_path=str(self.NORMALIZED_FILE),
            output_video_path=str(temp_file),
            write_frame_number=True
        )
        video_loader.process_video()
        video_loader.close_output()

        # swap the temp video inplace of the normalized video
        self.NORMALIZED_FILE.unlink()
        shutil.move(temp_file, self.NORMALIZED_FILE)

        self.extract_normalized_file_metadata()

    def extract_normalized_file_metadata(self):
        self.video.normalized_file = VideoFile.from_existing_file(
            root_path=self.folder_repo.root_path,
            file_path=self.NORMALIZED_FILE
        )
        self.videos_repository.store(self.video)
    
    def run_mediapipe(self):
        mediapipe = MediapipeProcessor(
            input_file=self.NORMALIZED_FILE,
            geometry_file=self.GEOMETRY_FILE,
            cropped_left_hand_folder=self.CROPPED_LEFT_HAND_FOLDER,
            cropped_right_hand_folder=self.CROPPED_RIGHT_HAND_FOLDER,
            cropped_face_folder=self.CROPPED_FACE_FOLDER,
        )
        mediapipe.run()
