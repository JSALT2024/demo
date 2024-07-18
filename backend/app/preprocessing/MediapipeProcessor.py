import sys
from pathlib import Path
from .FileFrameStream import FileFrameStream
from .InMemoryFrameStream import InMemoryFrameStream
from .FolderJpgFrameStream import FolderJpgFrameStream
from .ClipSplitter import ClipSplitter
from .Frame import Frame
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
        cropped_left_hand_folder: Path,
        cropped_right_hand_folder: Path,
        cropped_face_folder: Path,
        slicing_period_seconds=1.0
    ):
        self.input_file = input_file
        self.geometry_file = geometry_file
        self.cropped_left_hand_folder = cropped_left_hand_folder
        self.cropped_right_hand_folder = cropped_right_hand_folder
        self.cropped_face_folder = cropped_face_folder
        self.slicing_period_seconds = slicing_period_seconds

    def run(self):
        # load mediapipe models
        mdp_models = create_mediapipe_models("checkpoints/PoseEstimation")

        # open the video file
        file_frame_stream = FileFrameStream(self.input_file)

        # prepare the array for all array geometries
        frame_geometries: List[FrameGeometry] = []

        # prepare output steams for encoder crops
        cropped_left_hand_stream = FolderJpgFrameStream.create(
            self.cropped_left_hand_folder,
            framerate=file_frame_stream.framerate
        )
        cropped_right_hand_stream = FolderJpgFrameStream.create(
            self.cropped_right_hand_folder,
            framerate=file_frame_stream.framerate
        )
        cropped_face_stream = FolderJpgFrameStream.create(
            self.cropped_face_folder,
            framerate=file_frame_stream.framerate
        )

        # process the video file in fixed-size chunks
        splitter = ClipSplitter(
            in_stream=file_frame_stream,
            target_clip_length_seconds=self.slicing_period_seconds
        )
        chunk_start_frame = 0
        for chunk_index, chunk_stream in enumerate(splitter):
            chunk_frames = [frame.img for frame in chunk_stream]
            chunk_length = len(chunk_stream)
            prediction: dict = predict_pose(chunk_frames, mdp_models)

            # process keypoints
            for i in range(chunk_length): # for each frame in the chunk
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
            
            # process crops
            # (crops come in the original resolution taken from the frame)
            for i in range(chunk_length): # for each frame in the chunk
                cropped_left_hand_stream.write_frame(
                    frame=Frame(prediction["cropped_left_hand"][i]),
                    seek_to=chunk_start_frame + i
                )
                cropped_right_hand_stream.write_frame(
                    frame=Frame(prediction["cropped_right_hand"][i]),
                    seek_to=chunk_start_frame + i
                )
                cropped_face_stream.write_frame(
                    frame=Frame(prediction["cropped_face"][i]),
                    seek_to=chunk_start_frame + i
                )
            
            # update state
            chunk_start_frame += chunk_length

            # log
            print(f"Second {chunk_index + 1} was mediapiped.")

        # store frames geometry data
        with open(self.geometry_file, "w") as f:
            data = [frame.to_json() for frame in frame_geometries]
            json.dump(data, f)
