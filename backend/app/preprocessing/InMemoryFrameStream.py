from .FrameStream import FrameStream
from .Frame import Frame
from typing import List, Optional
import numpy as np
from pathlib import Path


class InMemoryFrameStream(FrameStream):
    def __init__(
        self,
        framerate: float,
        width: int,
        height: int
    ):
        self._framerate = framerate
        self._width = width
        self._height = height

        self._frames: List[Frame] = []
        self._next_frame_index = 0
    
    def from_stream(in_stream: FrameStream) -> "InMemoryFrameStream":
        """
        Creates an in-memory stream from another stream by reading it completely
        """
        out_stream = InMemoryFrameStream(
            framerate=in_stream.framerate,
            width=in_stream.width,
            height=in_stream.height
        )

        for frame in in_stream:
            out_stream.write_frame(frame)
        
        out_stream.seek(0)

        return out_stream

    @property
    def framerate(self) -> float:
        return self._framerate
    
    @property
    def width(self) -> int:
        return self._width
    
    @property
    def height(self) -> int:
        return self._height
    
    def _clamp_frame_index(self):
        if self._next_frame_index < 0:
            self._next_frame_index = 0
        if self._next_frame_index >= len(self._frames):
            self._next_frame_index = len(self._frames) - 1
    
    def seek(self, frame_index: int):
        self._next_frame_index = frame_index
        self._clamp_frame_index()
    
    def read_frame(self, advance_pointer=True) -> Optional[Frame]:
        if self._next_frame_index >= len(self._frames):
            return None
        
        frame = self._frames[self._next_frame_index]

        if advance_pointer:
            self._next_frame_index += 1
        
        return frame

    def write_frame(self, frame: Frame, advance_pointer=True):
        if frame.width != self.width or frame.height != self.height:
            raise Exception(
                "Frame resolution has to match the stream resolution"
            )
        
        if self._next_frame_index == len(self._frames):
            self._frames.append(frame)
        elif self._next_frame_index < len(self._frames):
            self._frames[self._next_frame_index] = frame
        else:
            raise Exception("Pointer points after the end of the video")
        
        if advance_pointer:
            self._next_frame_index += 1
    
    def __iter__(self):
        self.seek(0)
        return self

    def __next__(self) -> Frame:
        frame = self.read_frame()
        
        if frame is None:
            raise StopIteration
        
        return frame

    def __len__(self) -> int:
        return len(self._frames)
    
    def dump_npz(self, file_path: Path):
        file_path = file_path.with_suffix(".npz")
        frames = np.array(
            [frame.img for frame in self._frames],
            dtype=np.uint8
        )

        with open(file_path, "wb") as file:
            np.savez(
                file,
                frames=frames,
                framerate=self.framerate
            )
    
    @staticmethod
    def load_npz(file_path: Path) -> "InMemoryFrameStream":
        with open(file_path, "rb") as file:
            data = np.load(file)
            frames: np.ndarray = data["frames"]
            framerate: float = data["framerate"]

        stream = InMemoryFrameStream(
            framerate=framerate,
            width=frames.shape[2],
            height=frames.shape[1]
        )
        
        for i in range(frames.shape[0]):
            stream.write_frame(
                Frame(frames[i, :, :, :])
            )
        
        stream.seek(0)

        return stream
