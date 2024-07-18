from dataclasses import dataclass
import numpy as np
from typing import List, Optional


@dataclass
class FrameGeometry:
    """
    Contains geometry information about a single video frame.
    All the X, Y coordinates are in the pixel-space of the video frames.
    Is None if the pose was not detected.
    """
    
    pose_landmarks: Optional[np.ndarray]
    """
    Contains 33 pose landmarks from the mediapipe pose landmarker model.
    Each landmark consists of 4 numbers: [X, Y, Z, visibility].
    The raw mediapipe model returns an additional fifth "presence" value,
    which is not used so is omitted from the data matrix.
    
    https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
    https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf
    """

    sign_space: List[int]
    """
    Defines the signing space rectangle detected in the video frame
    in the form [X_min, Y_min, X_max, Y_max]. The numbers are rounded
    to integers because they were used to produce the crops
    for subsequent encoders. If no pose is detected, the signing space
    snaps such that it contains the entire video precisely.
    """

    def __post_init__(self):
        if self.pose_landmarks is not None:
            assert str(self.pose_landmarks.dtype) == "float64"
            assert self.pose_landmarks.shape == (33, 4)

        assert len(self.sign_space) == 4
        assert all((type(i) is int) for i in self.sign_space)
    
    def to_json(self) -> dict:
        return {
            "pose_landmarks": (
                None if self.pose_landmarks is None
                else self.pose_landmarks.tolist()
            ),
            "sign_space": self.sign_space,
        }
    
    @staticmethod
    def from_json(json: dict) -> "FrameGeometry":
        return FrameGeometry(
            pose_landmarks=(
                None if json["pose_landmarks"] is None
                else np.array(json["pose_landmarks"], np.float64)
            ),
            sign_space=[int(i) for i in json["sign_space"]],
        )
