import sys
import numpy as np
import requests
from typing import List
import cv2
import os


sys.path.append("models/PoseEstimation")
from predict_pose import predict_pose, create_mediapipe_models


def download_and_load_test_video() -> List[np.ndarray]:
    """
    Loads first 30 frames of the test video (and downloads the video if needed)
    """
    file_path = "checkpoints/PoseEstimation/testing-video.mp4"
    
    if not os.path.exists(file_path):
        url = "https://videos.pexels.com/video-files/5212084/"\
            "5212084-uhd_2560_1440_25fps.mp4"
        request = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(request.content)
    
    video_capture = cv2.VideoCapture(file_path)
    video_frames = [
        cv2.cvtColor(video_capture.read()[1], cv2.COLOR_BGR2RGB) # RGB!
        for _ in range(30)
    ]
    video_capture.release()

    return video_frames


def test_mediapipe():
    print("Loading mediapipe models...")
    models = create_mediapipe_models("checkpoints/PoseEstimation")

    # prepare dummy black 1 second video
    video = download_and_load_test_video()

    print("Running mediapipe models...")
    prediction = predict_pose(video, models)

    assert type(prediction) is dict
    assert len(prediction["cropped_images"]) == 30
    assert len(prediction["keypoints"]) == 30
    
    print("Mediapipe returns sensible results.")


if __name__ == "__main__":
    test_mediapipe()
