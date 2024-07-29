from typing import Optional
import numpy as np
from dataclasses import dataclass


@dataclass
class ClipVisualFeatures:
    """
    Holds the visual features extracted by all encoders about a single clip.
    """
    
    mae_features: Optional[np.ndarray] = None
    "MAE features for all clip frames"

    dino_features: Optional[np.ndarray] = None
    "DINO features for all clip frames"

    s2v_features: Optional[np.ndarray] = None
    "Sign2Vec features for the clip"
