from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np
from pathlib import Path
from .Clip import Clip
from .ClipVisualFeatures import ClipVisualFeatures


MAE_FEATURES_DIMENSION = 768
DINO_FEATURES_DIMENSION = 1152
S2V_FEATURES_DIMENSION = 768


@dataclass
class VideoVisualFeatures:
    """
    Holds visual features extracted by all encoders about an entire video.
    If the features have not yet been extracted, they will be set to None.
    """
    
    mae_features: Optional[np.ndarray] = None
    "MAE features for all video frames"

    dino_features: Optional[np.ndarray] = None
    "DINO features for all video frames"

    s2v_features: Optional[Dict[int, np.ndarray]] = None
    "Sign2Vec features separated into clips by the clip ID"

    def __post_init__(self):
        self.validate()
    
    def validate(self):
        if self.mae_features is not None:
            assert len(self.mae_features.shape) == 2
            assert self.mae_features.shape[1] == MAE_FEATURES_DIMENSION
            assert str(self.mae_features.dtype) == "float32"
        
        if self.dino_features is not None:
            assert len(self.dino_features.shape) == 2
            assert self.dino_features.shape[1] == DINO_FEATURES_DIMENSION
            assert str(self.dino_features.dtype) == "float32"

        if self.s2v_features is not None:
            for clip_features in self.s2v_features.values():
                assert len(clip_features.shape) == 2
                assert clip_features.shape[1] == S2V_FEATURES_DIMENSION
                assert str(clip_features.dtype) == "float32"

    def save_mae(self, mae_features_file: Path):
        if self.mae_features is None:
            if mae_features_file.is_file():
                mae_features_file.unlink()
        else:
            np.save(mae_features_file, self.mae_features)

    def save_dino(self, dino_features_file: Path):
        if self.dino_features is None:
            if dino_features_file.is_file():
                dino_features_file.unlink()
        else:
            np.save(dino_features_file, self.dino_features)
    
    def save_s2v(self, s2v_features_file: Path):
        if self.s2v_features is None:
            if s2v_features_file.is_file():
                s2v_features_file.unlink()
        else:
            np.savez(
                s2v_features_file,
                **{
                    str(clip_index): features
                    for clip_index, features in self.s2v_features.items()
                }
            )
    
    def save_all(
        self,
        mae_features_file: Path,
        dino_features_file: Path,
        s2v_features_file: Path
    ):
        self.save_mae(mae_features_file)
        self.save_dino(dino_features_file)
        self.save_s2v(s2v_features_file)

    def load_mae(self, mae_features_file: Path):
        if not mae_features_file.is_file():
            self.mae_features = None
        else:
            with open(mae_features_file, "rb") as file:
                self.mae_features = np.load(file)
                self.validate()
    
    def load_dino(self, dino_features_file: Path):
        if not dino_features_file.is_file():
            self.dino_features = None
        else:
            with open(dino_features_file, "rb") as file:
                self.dino_features = np.load(file)
                self.validate()
    
    def load_s2v(self, s2v_features_file: Path):
        if not s2v_features_file.is_file():
            self.s2v_features = None
        else:
            with open(s2v_features_file, "rb") as file:
                video_features: dict = np.load(file)
                self.s2v_features = {
                    int(clip_index_str): clip_features
                    for clip_index_str, clip_features in video_features.items()
                }
                self.validate()

    @staticmethod
    def load_all(
        mae_features_file: Path,
        dino_features_file: Path,
        s2v_features_file: Path
    ) -> "VideoVisualFeatures":
        features = VideoVisualFeatures()
        features.load_mae(mae_features_file)
        features.load_dino(dino_features_file)
        features.load_s2v(s2v_features_file)
        return features
    
    def select_clip(self, clip: Clip) -> ClipVisualFeatures:
        return ClipVisualFeatures(
            s2v_features=self.s2v_features[clip.clip_index],
            mae_features=self.mae_features[clip.frame_range, :],
            dino_features=self.dino_features[clip.frame_range, :],
        )
