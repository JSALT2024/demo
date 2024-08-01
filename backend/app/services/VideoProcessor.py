from .VideoFolderRepository import VideoFolderRepository
from .VideosRepository import VideosRepository
from ..domain.Video import Video
from ..domain.VideoFile import VideoFile
from ..preprocessing.VideoNormalizer import VideoNormalizer
from ..preprocessing.FrameEnumerator import FrameEnumerator
from ..preprocessing.MediapipeProcessor import MediapipeProcessor
from ..preprocessing.FixedLengthVideoClipper import FixedLengthVideoClipper
from ..encoding.MaeProcessor import MaeProcessor
from ..encoding.DinoProcessor import DinoProcessor
from ..encoding.Sign2VecProcessor import Sign2VecProcessor
from ..translation.SignLlavaTranslator import SignLlavaTranslator
from ..translation.SignLlavaCache import SignLlavaCache
import shutil
import torch
import logging
from typing import Optional


class VideoProcessor:
    """
    Performs all the video processing tasks after a video is uploaded to the
    server, including its translation by the LLM.
    """

    def __init__(
        self,
        video: Video,
        videos_repository: VideosRepository,
        video_folder: VideoFolderRepository,
        sign_llava_cache: SignLlavaCache,
        huggingface_token: Optional[str],
        logger: logging.Logger
    ):
        self.video = video
        self.videos_repository = videos_repository
        self.video_folder = video_folder
        self.sign_llava_cache = sign_llava_cache
        self.huggingface_token = huggingface_token
        self.logger = logger

        # check upload finished
        if video.uploaded_file is None:
            raise Exception(
                "Only a video that has already finished " +
                "uploading can be processed."
            )
    
    def run(self, force_all=False):
        """
        Runs all of the processing tasks. The force_all forces even
        the execution of phases that have already been executed before.
        """
        
        # initial preprocessing
        if not self.video_folder.NORMALIZED_FILE.exists() or force_all:
            self.normalize_uploaded_file()
            self.enumerate_normalized_file()

        # mediapipe
        if not self.video_folder.GEOMETRY_FILE.exists() or force_all:
            self.run_mediapipe()

        # clip splitting
        if not self.video_folder.CLIPS_COLLECTION_FILE.exists() or force_all:
            self.slice_into_clips()

        # encoders
        if not self.video_folder.MAE_FEATURES_FILE.exists() or force_all:
            self.run_mae()
        if not self.video_folder.DINO_FEATURES_FILE.exists() or force_all:
            self.run_dino()
        if not self.video_folder.S2V_FEATURES_FILE.exists() or force_all:
            self.run_sign2vec()

        # LLaVA
        self.run_llm_translation()

    def normalize_uploaded_file(self):
        self.logger.info("Normalizing video...")
        uploaded_file = self.video_folder.path(
            self.video.uploaded_file.file_path
        )
        normalizer = VideoNormalizer(
            input_video_path=str(uploaded_file),
            output_video_path=str(self.video_folder.NORMALIZED_FILE),
            fps_lower_bound=23, # because many videos are 23.98 FPS
            fps_higher_bound=30 # because many videos are 30 FPS
        )
        normalizer.process_video()
        normalizer.close_output()

        self.extract_normalized_file_metadata()
        
        self.logger.info("Normalization done!")

    def enumerate_normalized_file(self):
        self.logger.info("Enumerating normalized video...")
        temp_file = self.video_folder.NORMALIZED_FILE.with_stem(
            "temp_enumerated_file"
        )

        video_loader = FrameEnumerator(
            input_video_path=str(self.video_folder.NORMALIZED_FILE),
            output_video_path=str(temp_file),
            write_frame_number=True
        )
        video_loader.process_video()
        video_loader.close_output()

        # swap the temp video inplace of the normalized video
        self.video_folder.NORMALIZED_FILE.unlink()
        shutil.move(temp_file, self.video_folder.NORMALIZED_FILE)

        self.extract_normalized_file_metadata()

        self.logger.info("Enumeration done!")

    def extract_normalized_file_metadata(self):
        self.video.normalized_file = VideoFile.from_existing_file(
            root_path=self.video_folder.root_path,
            file_path=self.video_folder.NORMALIZED_FILE
        )
        self.videos_repository.store(self.video)
    
    def run_mediapipe(self):
        mediapipe = MediapipeProcessor(
            input_file=self.video_folder.NORMALIZED_FILE,
            geometry_file=self.video_folder.GEOMETRY_FILE,
            cropped_left_hand_folder=self.video_folder.CROPPED_LEFT_HAND_FOLDER,
            cropped_right_hand_folder=self.video_folder.CROPPED_RIGHT_HAND_FOLDER,
            cropped_face_folder=self.video_folder.CROPPED_FACE_FOLDER,
            cropped_images_folder=self.video_folder.CROPPED_IMAGES_FOLDER,
            logger=self.logger
        )
        mediapipe.run()
    
    def slice_into_clips(self):
        # This can later be replaced by a slicer that separates utterances
        # properly. This is just a minimal implementation to get things going.
        clip_length_seconds=5.0
        self.logger.info(
            f"Slicing the video into {clip_length_seconds} second clips..."
        )
        clipper = FixedLengthVideoClipper(
            normalized_video_file=self.video_folder.NORMALIZED_FILE,
            clip_length_seconds=clip_length_seconds
        )
        clips_collection = clipper.run()
        clips_collection.store(self.video_folder.CLIPS_COLLECTION_FILE)
        self.logger.info("Clips are now defined!")

    def run_mae(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        mae = MaeProcessor(
            device=device,
            cropped_images_folder=self.video_folder.CROPPED_IMAGES_FOLDER,
            mae_features_file=self.video_folder.MAE_FEATURES_FILE,
            logger=self.logger
        )
        mae.run()

    def run_dino(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        dino = DinoProcessor(
            device=device,
            cropped_face_folder=self.video_folder.CROPPED_FACE_FOLDER,
            cropped_left_hand_folder=self.video_folder.CROPPED_LEFT_HAND_FOLDER,
            cropped_right_hand_folder=self.video_folder.CROPPED_RIGHT_HAND_FOLDER,
            dino_features_file=self.video_folder.DINO_FEATURES_FILE,
            logger=self.logger
        )
        dino.run()
    
    def run_sign2vec(self):
        s2v = Sign2VecProcessor(
            geometry_file=self.video_folder.GEOMETRY_FILE,
            s2v_features_file=self.video_folder.S2V_FEATURES_FILE,
            clips_collection_file=self.video_folder.CLIPS_COLLECTION_FILE,
            logger=self.logger,
            huggingface_token=self.huggingface_token
        )
        s2v.run()

    def run_llm_translation(self):
        translator = SignLlavaTranslator(
            clips_collection_file=self.video_folder.CLIPS_COLLECTION_FILE,
            mae_features_file=self.video_folder.MAE_FEATURES_FILE,
            s2v_features_file=self.video_folder.S2V_FEATURES_FILE,
            dino_features_file=self.video_folder.DINO_FEATURES_FILE,
            sign_llava_cache=self.sign_llava_cache,
            logger=self.logger
        )
        translator.run()
