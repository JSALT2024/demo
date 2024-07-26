import numpy as np
import requests
import os
from ..preprocessing.VideoNormalizer import VideoNormalizer
from ..add_venv_bin_to_path import add_venv_bin_to_path
add_venv_bin_to_path()


def download_and_load_test_video() -> str:
    file_path = "models/ffmpeg/testing-video.mp4"
    
    if not os.path.exists(file_path):
        url = "https://videos.pexels.com/video-files/5212084/"\
            "5212084-uhd_2560_1440_25fps.mp4"
        request = requests.get(url)
        with open(file_path, "wb") as f:
            f.write(request.content)
    
    return file_path


def test_ffmpeg():
    print("Getting the test video for FFMPEG...")
    video_path = download_and_load_test_video()

    print("Running FFMPEG...")
    normalizer = VideoNormalizer(
        input_video_path=str(video_path),
        output_video_path=str(video_path + ".normalized.mp4"),
        fps_lower_bound=23,
        fps_higher_bound=30
    )
    normalizer.process_video()
    normalizer.close_output()

    print("FFMPEG finished without crashing.")


if __name__ == "__main__":
    test_ffmpeg()
