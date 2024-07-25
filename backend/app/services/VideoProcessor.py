from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from ..domain.VideoFile import VideoFile
from ..preprocessing.VideoNormalizer import VideoNormalizer
from ..preprocessing.FrameEnumerator import FrameEnumerator
from ..preprocessing.MediapipeProcessor import MediapipeProcessor
from ..preprocessing.FixedLengthClipSlicer import FixedLengthClipSlicer
from ..encoding.MaeProcessor import MaeProcessor
from ..encoding.DinoProcessor import DinoProcessor
from ..encoding.Sign2VecProcessor import Sign2VecProcessor
from pathlib import Path
import shutil
import torch
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
        self.CROPPED_IMAGES_FOLDER = self.path("cropped_images")
        self.CLIPS_COLLECTION_FILE = self.path("clips_collection.json")
        self.EMBEDDINGS_MAE_FILE = self.path("embeddings_mae.npy")
        self.EMBEDDINGS_S2V_FILE = self.path("embeddings_s2v.npy")
        self.EMBEDDINGS_DINO_FILE = self.path("embeddings_dino.npy")
    
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
        if not self.GEOMETRY_FILE.exists() and not force_all:
            self.run_mediapipe()

        # clip splitting
        if not self.CLIPS_COLLECTION_FILE.exists() and not force_all:
            self.slice_into_clips()

        # encoders
        if not self.EMBEDDINGS_MAE_FILE.exists() and not force_all:
            self.run_mae()
        if not self.EMBEDDINGS_S2V_FILE.exists() and not force_all:
            self.run_sign2vec()
        if not self.EMBEDDINGS_DINO_FILE.exists() and not force_all:
            self.run_dino()

        # LLaVA
        # TODO ...

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
            cropped_images_folder=self.CROPPED_IMAGES_FOLDER
        )
        mediapipe.run()
    
    def slice_into_clips(self):
        # This can later be replaced by a slicer that separates utterances
        # properly. This is just a minimal implementation to get things going.
        slicer = FixedLengthClipSlicer(
            normalized_video_file=self.NORMALIZED_FILE,
            clip_length_seconds=2.0 # TODO: increase to more seconds later!
        )
        clips_collection = slicer.run()
        clips_collection.store(self.CLIPS_COLLECTION_FILE)

    def run_mae(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        mae = MaeProcessor(
            device=device,
            cropped_images_folder=self.CROPPED_IMAGES_FOLDER,
            embeddings_mae_file=self.EMBEDDINGS_MAE_FILE
        )
        mae.run()
    
    def run_sign2vec(self):
        pass

    def run_dino(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dino = DinoProcessor(
            device=device,
            cropped_face_folder=self.CROPPED_FACE_FOLDER,
            cropped_left_hand_folder=self.CROPPED_LEFT_HAND_FOLDER,
            cropped_right_hand_folder=self.CROPPED_RIGHT_HAND_FOLDER,
            embeddings_dino_file=self.EMBEDDINGS_DINO_FILE
        )
        dino.run()
