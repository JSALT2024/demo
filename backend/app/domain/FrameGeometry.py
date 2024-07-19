from dataclasses import dataclass
import numpy as np
from typing import List, Optional


@dataclass
class FrameGeometry:
    """
    Contains geometry information about a single video frame.
    All the X, Y coordinates are in the pixel-space of the video frame.
    """
    
    pose_landmarks: Optional[np.ndarray]
    """
    Contains 33 pose landmarks from the mediapipe pose landmarker model.
    Each landmark consists of 4 numbers: [X, Y, Z, visibility].
    The raw mediapipe model returns an additional fifth "presence" value,
    which is not used so is omitted from the data matrix.
    Is None if the pose was not detected.
    
    https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#pose_landmarker_model
    https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf
    """

    right_hand_landmarks: Optional[np.ndarray]
    """
    Contains 21 hand landmarks from the mediapipe hand landmarker model.
    Each landmark consists of 4 numbers: [X, Y, Z, ?].
    Allegedly, the last number is a slot for visibility (to have the same format
    as for pose estimation), but it's not used by the hand landmarker
    so it's always set to zero.
    Is None if the hand was not detected.

    https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models
    https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf
    """

    left_hand_landmarks: Optional[np.ndarray]
    """
    Contains 21 hand landmarks from the mediapipe hand landmarker model.
    Each landmark consists of 4 numbers: [X, Y, Z, ?].
    Allegedly, the last number is a slot for visibility (to have the same format
    as for pose estimation), but it's not used by the hand landmarker
    so it's always set to zero.
    Is None if the hand was not detected.

    https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models
    https://storage.googleapis.com/mediapipe-assets/Model%20Card%20Hand%20Tracking%20(Lite_Full)%20with%20Fairness%20Oct%202021.pdf
    """

    face_landmarks: Optional[np.ndarray]
    """
    Contains 478 face landmarks from the mediapipe face mesh model.
    Each landmark consist of 4 numbers: [X, Y, Z, ?].
    Allegedly, the last number is a slot for visibility (to have the same format
    as for pose estimation), but it's not used by the hand landmarker
    so it's always set to zero.
    Is None if the face was not detected.

    https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker#models
    https://storage.googleapis.com/mediapipe-assets/MediaPipe%20BlazeFace%20Model%20Card%20(Short%20Range).pdf
    """

    sign_space: List[int]
    """
    Defines the signing space rectangle detected in the video frame
    in the form [X_min, Y_min, X_max, Y_max]. The numbers are rounded
    to integers because they were used to produce the crops
    for subsequent encoders. If no pose is detected, the signing space
    snaps such that it contains the entire video precisely.
    """

    right_hand_bbox: Optional[List[int]]
    """
    Defines the right hand bounding box rectangle detected in the video fram
    in the form [X_min, Y_min, X_max, Y_max]. The numbers are rounded
    to integers because they were used to produce the crops
    for subsequent encoders. Is None if no right hand is detected.
    """

    left_hand_bbox: Optional[List[int]]
    """
    Defines the left hand bounding box rectangle detected in the video fram
    in the form [X_min, Y_min, X_max, Y_max]. The numbers are rounded
    to integers because they were used to produce the crops
    for subsequent encoders. Is None if no left hand is detected.
    """

    face_bbox: Optional[List[int]]
    """
    Defines the face bounding box rectangle detected in the video fram
    in the form [X_min, Y_min, X_max, Y_max]. The numbers are rounded
    to integers because they were used to produce the crops
    for subsequent encoders. Is None if no face is detected.
    """

    def __post_init__(self):
        if self.pose_landmarks is not None:
            assert str(self.pose_landmarks.dtype) == "float64"
            assert self.pose_landmarks.shape == (33, 4)
        
        if self.right_hand_landmarks is not None:
            assert str(self.right_hand_landmarks.dtype) == "float64"
            assert self.right_hand_landmarks.shape == (21, 4)
        
        if self.left_hand_landmarks is not None:
            assert str(self.left_hand_landmarks.dtype) == "float64"
            assert self.left_hand_landmarks.shape == (21, 4)
        
        if self.face_landmarks is not None:
            assert str(self.face_landmarks.dtype) == "float64"
            assert self.face_landmarks.shape == (478, 4)

        assert len(self.sign_space) == 4
        assert all((type(i) is int) for i in self.sign_space)

        if self.right_hand_bbox is not None:
            assert len(self.right_hand_bbox) == 4
            assert all((type(i) is int) for i in self.right_hand_bbox)

        if self.left_hand_bbox is not None:
            assert len(self.left_hand_bbox) == 4
            assert all((type(i) is int) for i in self.left_hand_bbox)

        if self.face_bbox is not None:
            assert len(self.face_bbox) == 4
            assert all((type(i) is int) for i in self.face_bbox)
    
    def to_json(self) -> dict:
        # NOTE: we round the numbers when storing to JSON, because they are
        # mostly pixel-coordinates which don't need to be super precise and in
        # the JSON format the decimal numbers are very verbose otherwise.
        # The JSON file shrinks down to 40% of the non-rounded file size.
        return {
            "pose_landmarks": (
                None if self.pose_landmarks is None
                else self.pose_landmarks.round(decimals=2).tolist()
            ),
            "right_hand_landmarks": (
                None if self.right_hand_landmarks is None
                else self.right_hand_landmarks.round(decimals=2).tolist()
            ),
            "left_hand_landmarks": (
                None if self.left_hand_landmarks is None
                else self.left_hand_landmarks.round(decimals=2).tolist()
            ),
            "face_landmarks": (
                None if self.face_landmarks is None
                else self.face_landmarks.round(decimals=2).tolist()
            ),
            "sign_space": self.sign_space,
            "right_hand_bbox": self.right_hand_bbox,
            "left_hand_bbox": self.left_hand_bbox,
            "face_bbox": self.face_bbox
        }
    
    @staticmethod
    def from_json(json: dict) -> "FrameGeometry":
        return FrameGeometry(
            pose_landmarks=(
                None if json["pose_landmarks"] is None
                else np.array(json["pose_landmarks"], np.float64)
            ),
            right_hand_landmarks=(
                None if json["right_hand_landmarks"] is None
                else np.array(json["right_hand_landmarks"], np.float64)
            ),
            left_hand_landmarks=(
                None if json["left_hand_landmarks"] is None
                else np.array(json["left_hand_landmarks"], np.float64)
            ),
            face_landmarks=(
                None if json["face_landmarks"] is None
                else np.array(json["face_landmarks"], np.float64)
            ),
            sign_space=[int(i) for i in json["sign_space"]],
            right_hand_bbox=(
                None if json["right_hand_bbox"] is None
                else [int(i) for i in json["right_hand_bbox"]]
            ),
            left_hand_bbox=(
                None if json["left_hand_bbox"] is None
                else [int(i) for i in json["left_hand_bbox"]]
            ),
            face_bbox=(
                None if json["face_bbox"] is None
                else [int(i) for i in json["face_bbox"]]
            )
        )
