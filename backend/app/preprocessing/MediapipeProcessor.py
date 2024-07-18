import sys
from pathlib import Path
from .FileFrameStream import FileFrameStream
from .InMemoryFrameStream import InMemoryFrameStream
from .FolderJpgFrameStream import FolderJpgFrameStream
from .ClipSplitter import ClipSplitter
from .Frame import Frame
from ..domain.FrameGeometry import FrameGeometry
from typing import List, Any, Optional
import json
import numpy as np
import cv2
import queue
import threading
import time


sys.path.append("models/PoseEstimation")
from predict_pose import predict_pose, create_mediapipe_models


class ChunkJob:
    def __init__(
        self,
        source_framerate: float,
        frame_geometries: List[Optional[FrameGeometry]],
        cropped_left_hand_folder: Path,
        cropped_right_hand_folder: Path,
        cropped_face_folder: Path,
        chunk_stream: InMemoryFrameStream,
        chunk_start_frame: int
    ):
        self.source_framerate = source_framerate
        self.frame_geometries = frame_geometries
        self.cropped_left_hand_folder = cropped_left_hand_folder
        self.cropped_right_hand_folder = cropped_right_hand_folder
        self.cropped_face_folder = cropped_face_folder
        self.chunk_stream = chunk_stream
        self.chunk_start_frame = chunk_start_frame

        self.chunk_length = len(self.chunk_stream)
        self.chunk_end_frame = chunk_start_frame + self.chunk_length

    def run(self, mediapipe_models):
        prediction: dict = predict_pose(
            [frame.img for frame in self.chunk_stream],
            mediapipe_models
        )

        # process keypoints
        for i in range(self.chunk_length):
            self.frame_geometries[self.chunk_start_frame + i] = (
                self.get_frame_geometry(prediction, i)
            )
        
        # process crops
        self.store_crops(prediction)

        print(
            f"Frames {self.chunk_start_frame}-{self.chunk_end_frame} " +
            "were mediapiped."
        )
    
    def get_frame_geometry(
        self,
        prediction: dict,
        chunk_frame_index: int
    ) -> FrameGeometry:
        keypoints: dict = prediction["keypoints"][chunk_frame_index]

        def nullify(landmarks):
            if len(landmarks) == 0:
                return None
            return landmarks

        # build up the geometry data
        return FrameGeometry(
            # TODO: not detected pose?
            pose_landmarks=nullify(keypoints["pose_landmarks"]),
            # TODO: hands and face landmarks
            # TODO: signing space bbox
            sign_space=[
                # convert to python int from np.int64
                int(c) for c in prediction["sign_space"][chunk_frame_index]
            ],
            # TODO: hand crops bboxes
            # TODO: face crop bbox
        )
    
    def store_crops(self, prediction: dict):
        # NOTE: crops come in the original resolution taken from the frame,
        # so they are heterogenous in resolution (but always square)
        # DINO accepts 56x56 images, so I normalize to those.
        # MAE accepts 224x224 images, so I normalize to those.
        DINO_SIZE = 56
        MAE_SIZE = 224

        def normalize(img: np.ndarray, target_size: int) -> Frame:
            return Frame(
                cv2.resize(img, dsize=(target_size, target_size))
            )

        # prepare output streams for the crops
        # (here, for each chunk, because the stream has the current frame state
        # which would cause race condition if accessed concurrently)
        cropped_left_hand_stream = FolderJpgFrameStream.create(
            self.cropped_left_hand_folder,
            framerate=self.source_framerate,
            width=DINO_SIZE, height=DINO_SIZE
        )
        cropped_right_hand_stream = FolderJpgFrameStream.create(
            self.cropped_right_hand_folder,
            framerate=self.source_framerate,
            width=DINO_SIZE, height=DINO_SIZE
        )
        cropped_face_stream = FolderJpgFrameStream.create(
            self.cropped_face_folder,
            framerate=self.source_framerate,
            width=DINO_SIZE, height=DINO_SIZE
        )

        # process each frame in the chunk
        for i in range(self.chunk_length):
            cropped_left_hand_stream.write_frame(
                normalize(prediction["cropped_left_hand"][i], DINO_SIZE),
                seek_to=self.chunk_start_frame + i
            )
            cropped_right_hand_stream.write_frame(
                normalize(prediction["cropped_right_hand"][i], DINO_SIZE),
                seek_to=self.chunk_start_frame + i
            )
            cropped_face_stream.write_frame(
                normalize(prediction["cropped_face"][i], DINO_SIZE),
                seek_to=self.chunk_start_frame + i
            )


class Worker:
    def __init__(self, job_queue: queue.Queue):
        self.job_queue = job_queue
        self.thread = threading.Thread(
            target=lambda: self.main(),
            daemon=True
        )
    
    def start(self):
        self.thread.start()

    def main(self):
        # load mediapipe models
        mediapipe_models = create_mediapipe_models("checkpoints/PoseEstimation")

        while True:
            job = self.job_queue.get()
            
            # stops the worker
            if job is None:
                return
            
            # runs the job
            job.run(mediapipe_models)

    def join(self):
        self.thread.join()


class MediapipeProcessor:
    def __init__(
        self,
        input_file: Path,
        geometry_file: Path,
        cropped_left_hand_folder: Path,
        cropped_right_hand_folder: Path,
        cropped_face_folder: Path,
        chunking_period_seconds=1.0,
        parallel_worker_count=8
    ):
        self.input_file = input_file
        self.geometry_file = geometry_file
        self.cropped_left_hand_folder = cropped_left_hand_folder
        self.cropped_right_hand_folder = cropped_right_hand_folder
        self.cropped_face_folder = cropped_face_folder
        self.chunking_period_seconds = chunking_period_seconds
        self.parallel_worker_count = parallel_worker_count

    def run(self):
        # open the video file
        file_frame_stream = FileFrameStream(self.input_file)

        # prepare the array for all array geometries
        frame_geometries: List[Optional[FrameGeometry]] = []

        # start the worker system
        job_queue = queue.Queue(maxsize=1)
        workers = [
            Worker(job_queue) for _ in range(self.parallel_worker_count)
        ]
        for w in workers:
            w.start()

        # process the video file in fixed-size chunks
        splitter = ClipSplitter(
            in_stream=file_frame_stream,
            target_clip_length_seconds=self.chunking_period_seconds
        )
        chunk_start_frame = 0
        for chunk_stream in splitter:
            # create a job and enqueue it
            job = ChunkJob(
                source_framerate=file_frame_stream.framerate,
                frame_geometries=frame_geometries,
                cropped_left_hand_folder=self.cropped_left_hand_folder,
                cropped_right_hand_folder=self.cropped_right_hand_folder,
                cropped_face_folder=self.cropped_face_folder,
                chunk_stream=chunk_stream,
                chunk_start_frame=chunk_start_frame
            )
            frame_geometries += [None] * len(chunk_stream) # allocate more items
            job_queue.put(job, block=True) # blocks if all workers busy
            
            # update state
            chunk_start_frame += job.chunk_length
        
        # terminate all workers
        for _ in range(self.parallel_worker_count):
            job_queue.put(None, block=True)
        for w in workers:
            w.join()
        
        # check that all frame geometries were created
        assert all(g is not None for g in frame_geometries)

        # store frames geometry data
        with open(self.geometry_file, "w") as f:
            data = [frame.to_json() for frame in frame_geometries]
            json.dump(data, f)
