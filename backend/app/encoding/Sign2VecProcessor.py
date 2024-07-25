import torch
import sys
from pathlib import Path
import numpy as np
import sys
from typing import Optional, List, Dict
from ..domain.FrameGeometry import FrameGeometry
from ..domain.ClipsCollection import ClipsCollection
import json


sys.path.append("models/sign2vec")
from sign2vec.modeling_sign2vec import Sign2VecModel
from sign2vec.feature_extraction_sign2vec import Sign2VecFeatureExtractor


class Sign2VecProcessor:
    def __init__(
        self,
        geometry_file: Path,
        embeddings_s2v_file: Path,
        clips_collection_file: Path,
        huggingface_token: Optional[str] = None
    ):
        self.geometry_file = geometry_file
        self.embeddings_s2v_file = embeddings_s2v_file
        self.clips_collection_file = clips_collection_file

        self.huggingface_token = huggingface_token
        self.model_name = "karahansahin/sign2vec-yasl-mc-sc-64-2-d1-decay"
        self.embedding_dimension = 768

    def run(self):
        print("Loading the Sign2Vec model...")
        model = Sign2VecModel.from_pretrained(
            self.model_name,
            token=self.huggingface_token
        )
        feature_extractor = Sign2VecFeatureExtractor()

        # load the input data
        frame_geometries = self.load_frame_geometries()
        clips_collection = ClipsCollection.load(self.clips_collection_file)
        assert len(frame_geometries) == len(clips_collection.clip_index_lookup)

        # prepare the output embeddings matrices
        all_embeddings: Dict[int, np.ndarray] = {}

        def coalesce(landmarks: Optional[np.ndarray], size: int) -> np.ndarray:
            "Replaces None with zeros matrix"
            if landmarks is not None:
                return landmarks
            return np.zeros(shape=(size, 4), dtype=np.float64)

        # run sign2vec for each clip
        for clip_index, clip in enumerate(clips_collection.clips):
            clip_geometries = frame_geometries[
                clip.start_frame : clip.start_frame+clip.frame_count
            ]
            sample_pose = {
                "pose_landmarks": np.stack(
                    [coalesce(g.pose_landmarks, 33) for g in clip_geometries],
                    axis=0
                ),
                "right_hand_landmarks": np.stack(
                    [coalesce(g.right_hand_landmarks, 21) for g in clip_geometries],
                    axis=0
                ),
                "left_hand_landmarks": np.stack(
                    [coalesce(g.left_hand_landmarks, 21) for g in clip_geometries],
                    axis=0
                ),
                "face_landmarks": np.stack(
                    [coalesce(g.face_landmarks, 478) for g in clip_geometries],
                    axis=0
                ),
            }

            inputs = feature_extractor(sample_pose)
            features = inputs["input_values"][0]
            features = torch.tensor(features).float()
            features = features.transpose(1, 2)
            out = model(features)
            sign2vec_features = out.last_hidden_state.detach().cpu().numpy()[0]

            assert len(sign2vec_features.shape) == 2
            assert sign2vec_features.shape[1] == self.embedding_dimension
            assert sign2vec_features.shape[0] <= len(clip_geometries)
            assert str(sign2vec_features.dtype) == "float32"

            all_embeddings[clip_index] = sign2vec_features

            print(f"Clip {clip_index} was Sign2Vec'd...")
        
        # save the embeddings data
        np.savez(
            self.embeddings_s2v_file,
            **{
                f"clip_{clip_index}": embeddings
                for clip_index, embeddings in all_embeddings.items()
            }
        )
        print("S2V embeddings are saved. S2V done.")

    
    def load_frame_geometries(self) -> List[FrameGeometry]:
        with open(self.geometry_file, "r") as f:
            data = json.load(f)
        return [FrameGeometry.from_json(d) for d in data]
