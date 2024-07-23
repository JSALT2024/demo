import torch
import sys
from pathlib import Path
import numpy as np
import sys
from typing import Optional, List
from ..domain.FrameGeometry import FrameGeometry
import json


sys.path.append("models/sign2vec")
from sign2vec.modeling_sign2vec import Sign2VecModel
from sign2vec.feature_extraction_sign2vec import Sign2VecFeatureExtractor


class Sign2VecProcessor:
    def __init__(
        self,
        device: torch.device,
        geometry_file: Path,
        embeddings_s2v_file: Path,
        batching_period_seconds=10.0,
        huggingface_token: Optional[str] = None
    ):
        self.device = device
        self.geometry_file = geometry_file
        self.embeddings_s2v_file = embeddings_s2v_file
        self.batching_period_seconds = batching_period_seconds

        self.huggingface_token = huggingface_token
        self.model_name = "karahansahin/sign2vec-yasl-mc-sc-64-2-d1-decay"

    def run(self):
        print("Loading the Sign2Vec model...")
        model = Sign2VecModel.from_pretrained(
            self.model_name,
            token=self.huggingface_token
        )
        feature_extractor = Sign2VecFeatureExtractor()

        # load the input geometries
        frame_geometries = self.load_frame_geometries()

        # prepare the output embeddings matrix
        # all_embeddings = np.zeros(shape=(total_frames, 768), dtype=np.float32)
    
    def load_frame_geometries(self) -> List[FrameGeometry]:
        with open(self.geometry_file, "r") as f:
            data = json.load(f)
        return [FrameGeometry.from_json(d) for d in data]
