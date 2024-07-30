import torch
import sys
from pathlib import Path
from ..video.FolderJpgFrameStream import FolderJpgFrameStream
from ..video.FrameStreamChunker import FrameStreamChunker
from ..domain.VideoVisualFeatures \
    import VideoVisualFeatures, DINO_FEATURES_DIMENSION
import numpy as np
import logging


sys.path.append("models/DINOv2/predict")
import predict_dino


DINO_FACE_CHECKPOINT = \
    "checkpoints/DINOv2/face_dinov2_vits14_reg_teacher_checkpoint.pth"
DINO_HAND_CHECKPOINT = \
    "checkpoints/DINOv2/hand_dinov2_vits14_reg_teacher_checkpoint.pth"


class DinoProcessor:
    def __init__(
        self,
        device: torch.device,
        cropped_face_folder: Path,
        cropped_left_hand_folder: Path,
        cropped_right_hand_folder: Path,
        dino_features_file: Path,
        logger: logging.Logger,
        batching_period_seconds=1.0
    ):
        self.device = device
        self.cropped_face_folder = cropped_face_folder
        self.cropped_left_hand_folder = cropped_left_hand_folder
        self.cropped_right_hand_folder = cropped_right_hand_folder
        self.dino_features_file = dino_features_file
        self.logger = logger
        self.batching_period_seconds = batching_period_seconds

    def run(self):
        self.logger.info("Loading the DINO models...")
        face_model = predict_dino.create_dino_model(DINO_FACE_CHECKPOINT)
        hand_model = predict_dino.create_dino_model(DINO_HAND_CHECKPOINT)
        face_model.to(self.device)
        hand_model.to(self.device)

        # load the cropped images folder
        cropped_face_stream = FolderJpgFrameStream.open(
            self.cropped_face_folder
        )
        cropped_left_hand_stream = FolderJpgFrameStream.open(
            self.cropped_left_hand_folder
        )
        cropped_right_hand_stream = FolderJpgFrameStream.open(
            self.cropped_right_hand_folder
        )

        # get the total number of frames
        total_frames: int = len(cropped_face_stream)
        assert len(cropped_left_hand_stream) == total_frames
        assert len(cropped_right_hand_stream) == total_frames

        # prepare the output matrix
        visual_features = VideoVisualFeatures(
            dino_features=np.zeros(
                shape=(total_frames, DINO_FEATURES_DIMENSION),
                dtype=np.float32
            )
        )

        # process the video file in fixed-size batches
        self.logger.info("Processing frames with DINO...")
        face_chunker = FrameStreamChunker(
            in_stream=cropped_face_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        left_hand_chunker = FrameStreamChunker(
            in_stream=cropped_left_hand_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        right_hand_chunker = FrameStreamChunker(
            in_stream=cropped_right_hand_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        chunk_start_frame = 0
        for face_chunk_stream, left_hand_chunk_stream, right_hand_chunk_stream \
        in zip(face_chunker, left_hand_chunker, right_hand_chunker):
            face_images = [frame.img for frame in face_chunk_stream]
            left_hand_images = [frame.img for frame in left_hand_chunk_stream]
            right_hand_images = [frame.img for frame in right_hand_chunk_stream]
            
            face_features = predict_dino.dino_predict(
                face_images, face_model,
                predict_dino.transform_dino, self.device
            )
            left_features = predict_dino.dino_predict(
                left_hand_images, hand_model,
                predict_dino.transform_dino, self.device
            )
            right_features = predict_dino.dino_predict(
                right_hand_images, hand_model,
                predict_dino.transform_dino, self.device
            )
            chunk_features = np.concatenate(
                [face_features, left_features, right_features],
                1
            )

            chunk_size = len(face_chunk_stream)
            assert chunk_size == len(left_hand_chunk_stream)
            assert chunk_size == len(right_hand_chunk_stream)

            frame_from = chunk_start_frame
            frame_to = chunk_start_frame + chunk_size
            visual_features.dino_features[frame_from:frame_to] = chunk_features
            self.logger.info(f"Frames {frame_from}-{frame_to} were DINOed.")

            # update the state
            chunk_start_frame += chunk_size

        # save the features data
        visual_features.save_dino(self.dino_features_file)
        self.logger.info("DINO features are saved. DINO done.")
