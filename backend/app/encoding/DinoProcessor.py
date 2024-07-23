import torch
import sys
from pathlib import Path
from ..preprocessing.FolderJpgFrameStream import FolderJpgFrameStream
from ..preprocessing.ClipSplitter import ClipSplitter
import numpy as np


sys.path.append("models/DINOv2/predict")
import predict_dino


class DinoProcessor:
    def __init__(
        self,
        device: torch.device,
        cropped_face_folder: Path,
        cropped_left_hand_folder: Path,
        cropped_right_hand_folder: Path,
        embeddings_dino_file: Path,
        batching_period_seconds=1.0
    ):
        self.device = device
        self.cropped_face_folder = cropped_face_folder
        self.cropped_left_hand_folder = cropped_left_hand_folder
        self.cropped_right_hand_folder = cropped_right_hand_folder
        self.embeddings_dino_file = embeddings_dino_file
        self.batching_period_seconds = batching_period_seconds

        self.face_checkpoint = "checkpoints/DINOv2/face_dinov2_vits14_reg_teacher_checkpoint.pth"
        self.hand_checkpoint = "checkpoints/DINOv2/hand_dinov2_vits14_reg_teacher_checkpoint.pth"

    def run(self):
        print("Loading the DINO models...")
        face_model = predict_dino.create_dino_model(self.face_checkpoint)
        hand_model = predict_dino.create_dino_model(self.hand_checkpoint)
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
        all_embeddings = np.zeros(shape=(total_frames, 1152), dtype=np.float32)

        # process the video file in fixed-size batches
        print("Processing frames with DINO...")
        face_splitter = ClipSplitter(
            in_stream=cropped_face_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        left_hand_splitter = ClipSplitter(
            in_stream=cropped_left_hand_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        right_hand_splitter = ClipSplitter(
            in_stream=cropped_right_hand_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        chunk_start_frame = 0
        for face_chunk_stream, left_hand_chunk_stream, right_hand_chunk_stream \
        in zip(face_splitter, left_hand_splitter, right_hand_splitter):
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
            chunk_embeddings = np.concatenate(
                [face_features, left_features, right_features],
                1
            )

            chunk_size = len(face_chunk_stream)
            assert chunk_size == len(left_hand_chunk_stream)
            assert chunk_size == len(right_hand_chunk_stream)

            frame_from = chunk_start_frame
            frame_to = chunk_start_frame + chunk_size
            all_embeddings[frame_from:frame_to] = chunk_embeddings
            print(f"Frames {frame_from}-{frame_to} were DINOed.")

            # update the state
            chunk_start_frame += chunk_size

        # save the embeddings data
        np.save(self.embeddings_dino_file, all_embeddings)
        print("DINO embeddings are saved. DINO done.")
