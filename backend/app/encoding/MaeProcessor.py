import torch
import sys
from pathlib import Path
from ..preprocessing.FolderJpgFrameStream import FolderJpgFrameStream
from ..preprocessing.ClipSplitter import ClipSplitter
from ..domain.VideoVisualFeatures \
    import VideoVisualFeatures, MAE_FEATURES_DIMENSION
import numpy as np


sys.path.append("models/MAE/mae")
import predict_mae


MAE_ARCHITECTURE = "vit_base_patch16"
MAE_CHECKPOINT = "checkpoints/MAE/vit_base_16_16-07_21-52-12_checkpoint-440.pth"


class MaeProcessor:
    def __init__(
        self,
        device: torch.device,
        cropped_images_folder: Path,
        mae_features_file: Path,
        batching_period_seconds=1.0,
    ):
        self.device = device
        self.cropped_images_folder = cropped_images_folder
        self.mae_features_file = mae_features_file
        self.batching_period_seconds = batching_period_seconds

    def run(self):
        print("Loading the MAE model...")
        model = predict_mae.create_mae_model(MAE_ARCHITECTURE, MAE_CHECKPOINT)
        model = model.to(self.device)

        # load the cropped images folder
        cropped_images_stream = FolderJpgFrameStream.open(
            self.cropped_images_folder
        )
        total_frames: int = len(cropped_images_stream)

        # prepare the output matrix
        visual_features = VideoVisualFeatures(
            mae_features=np.zeros(
                shape=(total_frames, MAE_FEATURES_DIMENSION),
                dtype=np.float32
            )
        )

        # process the video file in fixed-size batches
        print("Processing frames with MAE...")
        splitter = ClipSplitter(
            in_stream=cropped_images_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        chunk_start_frame = 0
        for chunk_stream in splitter:
            images = [frame.img for frame in chunk_stream]
            chunk_features = predict_mae.mae_predict(
                images,
                model,
                predict_mae.transform_mae,
                self.device
            )

            chunk_size = len(chunk_stream)
            frame_from = chunk_start_frame
            frame_to = chunk_start_frame + chunk_size
            visual_features.mae_features[frame_from:frame_to] = chunk_features
            print(f"Frames {frame_from}-{frame_to} were MAE'd.")

            # update the state
            chunk_start_frame += chunk_size

        # save the features data
        visual_features.save_mae(self.mae_features_file)
        print("MAE features are saved. MAE done.")
