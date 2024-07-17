import sys
from pathlib import Path
from .FileFrameStream import FileFrameStream
from .InMemoryFrameStream import InMemoryFrameStream
from .ClipSplitter import ClipSplitter
from ..domain.FrameGeometry import FrameGeometry
from typing import List
import json


sys.path.append("models/PoseEstimation")
from predict_pose import predict_pose, create_mediapipe_models


class MediapipeProcessor:
    def __init__(
        self,
        input_file: Path,
        geometry_file: Path,
        slicing_period_seconds=1.0
    ):
        self.input_file = input_file
        self.geometry_file = geometry_file
        self.slicing_period_seconds = slicing_period_seconds

    def run(self):
        # load mediapipe models
        mdp_models = create_mediapipe_models("checkpoints/PoseEstimation")

        # open the video file
        file_frame_stream = FileFrameStream(self.input_file)

        # prepare the array for all array geometries
        frame_geometries: List[FrameGeometry] = []

        # process the video file in fixed-size chunks
        splitter = ClipSplitter(
            in_stream=file_frame_stream,
            target_clip_length_seconds=self.slicing_period_seconds
        )
        for chunk_index, chunk_stream in enumerate(splitter):
            chunk_frames = [frame.img for frame in chunk_stream]
            prediction: dict = predict_pose(chunk_frames, mdp_models)

            # process keypoints
            for i in range(len(chunk_stream)): # for each frame in the chunk
                keypoints: dict = prediction["keypoints"][i]
                frame_geometry = FrameGeometry(
                    # TODO: not detected pose?
                    pose_landmarks=keypoints["pose_landmarks"],
                    # TODO: hands and face landmarks
                    # TODO: signing space bbox
                    sign_space=[
                        # convert to python int from np.int64
                        int(c) for c in prediction["sign_space"][i]
                    ],
                    # TODO: hand crops bboxes
                    # TODO: face crop bbox
                )
                frame_geometries.append(frame_geometry)

            # TODO: DEBUG (just the first second)
            # if chunk_index > 5:
            #     break
            print(f"Second {chunk_index + 1} was mediapiped.")

        # store frames geometry data
        with open(self.geometry_file, "w") as f:
            data = [frame.to_json() for frame in frame_geometries]
            json.dump(data, f)
