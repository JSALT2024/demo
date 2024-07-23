import torch
import sys
from pathlib import Path
from ..preprocessing.FolderJpgFrameStream import FolderJpgFrameStream
from ..preprocessing.ClipSplitter import ClipSplitter
import numpy as np


sys.path.append("models/MAE/mae")
import predict_mae


class MaeProcessor:
    def __init__(
        self,
        device: torch.device,
        cropped_images_folder: Path,
        embeddings_mae_file: Path,
        batching_period_seconds=1.0,
    ):
        self.device = device
        self.cropped_images_folder = cropped_images_folder
        self.embeddings_mae_file = embeddings_mae_file
        self.batching_period_seconds = batching_period_seconds

        self.architecture = "vit_base_patch16"
        self.checkpoint_path = "checkpoints/MAE/vit_base_16_16-07_21-52-12_checkpoint-440.pth"

    def run(self):
        print("Loading the MAE model...")
        model = predict_mae.create_mae_model(
            self.architecture,
            self.checkpoint_path
        )
        model = model.to(self.device)

        # load the cropped images folder
        cropped_images_stream = FolderJpgFrameStream.open(
            self.cropped_images_folder
        )
        total_frames: int = len(cropped_images_stream)

        # prepare the output matrix
        all_embeddings = np.zeros(shape=(total_frames, 768), dtype=np.float32)

        # process the video file in fixed-size batches
        print("Processing frames with MAE...")
        splitter = ClipSplitter(
            in_stream=cropped_images_stream,
            target_clip_length_seconds=self.batching_period_seconds
        )
        chunk_start_frame = 0
        for chunk_stream in splitter:
            images = [frame.img for frame in chunk_stream]
            chunk_embeddings = predict_mae.mae_predict(
                images,
                model,
                predict_mae.transform_mae,
                self.device
            )

            chunk_size = len(chunk_stream)
            frame_from = chunk_start_frame
            frame_to = chunk_start_frame + chunk_size
            all_embeddings[frame_from:frame_to] = chunk_embeddings
            print(f"Frames {frame_from}-{frame_to} were MAE'd.")

            # update the state
            chunk_start_frame += chunk_size

        # save the embeddings data
        np.save(self.embeddings_mae_file, all_embeddings)
        print("MAE embeddings are saved. MAE done.")
