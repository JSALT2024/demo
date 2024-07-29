import torch
import sys
from pathlib import Path
import numpy as np
import sys
from typing import Optional
from ..domain.FrameGeometry import FrameGeometry
from ..domain.ClipsCollection import ClipsCollection
from ..domain.VideoVisualFeatures \
    import VideoVisualFeatures, S2V_FEATURES_DIMENSION
import logging


sys.path.append("models/sign2vec")
from sign2vec.modeling_sign2vec import Sign2VecModel
from sign2vec.feature_extraction_sign2vec import Sign2VecFeatureExtractor


S2V_MODEL_NAME = "karahansahin/sign2vec-yasl-mc-sc-64-2-d1"


class Sign2VecProcessor:
    def __init__(
        self,
        geometry_file: Path,
        s2v_features_file: Path,
        clips_collection_file: Path,
        huggingface_token: Optional[str] = None
    ):
        self.geometry_file = geometry_file
        self.s2v_features_file = s2v_features_file
        self.clips_collection_file = clips_collection_file
        self.huggingface_token = huggingface_token

    def run(self):
        print("Loading the Sign2Vec model...")
        model = Sign2VecModel.from_pretrained(
            S2V_MODEL_NAME,
            token=self.huggingface_token
        )
        feature_extractor = Sign2VecFeatureExtractor()

        # load the input data
        frame_geometries = FrameGeometry.list_from_json(self.geometry_file)
        clips_collection = ClipsCollection.load(self.clips_collection_file)
        assert len(frame_geometries) == len(clips_collection.clip_index_lookup)

        # prepare the output embeddings matrices
        visual_features = VideoVisualFeatures(s2v_features={})

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

            # print("S2V SAMPLE POSE:", { k: len(v) for k, v in sample_pose.items() })
            # print("S2V INPUTS:", inputs)
            # print("S2V INPUTS SHAPE:", inputs["input_values"][0].shape)

            try:
                out = model(features)
                sign2vec_features = out.last_hidden_state.detach().cpu().numpy()[0]

                # print("S2V OUTPUT:", out)
                # print("S2V FEATURES:", sign2vec_features.shape, sign2vec_features)
                # exit()
            except RuntimeError as e:
                # survive an error and pretend there was no S2V output
                sign2vec_features = np.zeros(
                    shape=(0, S2V_FEATURES_DIMENSION),
                    dtype=np.float32
                )
                logging.exception(f"SIGN2VEC Exception in clip {clip_index}:")

            visual_features.s2v_features[clip_index] = sign2vec_features

            print(f"Clip {clip_index} was Sign2Vec'd...")
        
        # save the features data
        visual_features.validate()
        visual_features.save_s2v(self.s2v_features_file)
        print("S2V features are saved. S2V done.")
