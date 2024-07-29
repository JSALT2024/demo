from .FrameStream import FrameStream
from .Frame import Frame
from typing import Optional
from pathlib import Path
import json
import shutil
import cv2
import glob


META_FILE = "_FolderJpgFrameStream.json"


class FolderJpgFrameStream(FrameStream):
    def __init__(
        self,
        framerate: float,
        width: Optional[int],
        height: Optional[int],
        folder_path: Path
    ):
        self._framerate = framerate
        self._width = width
        self._height = height

        self._folder_path = folder_path
        self._next_frame_index = 0
    
    @property
    def is_heterogenous(self) -> bool:
        """True if all the frames must have the same resolution"""
        return self._width is not None and self._height is not None
    
    @staticmethod
    def create(
        folder_path: Path,
        framerate: float,
        width: Optional[int] = None,
        height: Optional[int] = None,
        clear_if_exists=False,
    ) -> "FolderJpgFrameStream":
        # clear the folder if it exists
        if clear_if_exists and folder_path.is_dir():
            shutil.rmtree(folder_path)
        
        # create the folder if it does not exist
        if not folder_path.is_dir():
            folder_path.mkdir()
        
        # create the stream
        stream = FolderJpgFrameStream(
            framerate=framerate,
            width=width,
            height=height,
            folder_path=folder_path
        )

        # write the meta file
        stream._write_meta_file()

        return stream

    @staticmethod
    def open(folder_path: Path) -> "FolderJpgFrameStream":
        # read the meta file
        with open(folder_path / META_FILE, "r") as f:
            meta: dict = json.load(f)
            assert type(meta) is dict
        
        # create the stream instance
        return FolderJpgFrameStream(
            framerate=float(meta["framerate"]),
            width=None if meta["width"] is None else int(meta["width"]),
            height=None if meta["height"] is None else int(meta["height"]),
            folder_path=folder_path
        )

    def _write_meta_file(self):
        with open(self._folder_path / META_FILE, "w") as f:
            json.dump({
                "framerate": self._framerate,
                "width": self._width,
                "height": self._height
            }, f)

    @property
    def framerate(self) -> float:
        return self._framerate
    
    @property
    def width(self) -> int:
        if self._width is None:
            raise Exception("Heterogenous stream doesn't have fixed frame size")
        return self._width
    
    @property
    def height(self) -> int:
        if self._height is None:
            raise Exception("Heterogenous stream doesn't have fixed frame size")
        return self._height
    
    def seek(self, frame_index: int):
        self._next_frame_index = frame_index
    
    def _frame_path(self, frame_index: int) -> Path:
        return self._folder_path / f"frame_{str(frame_index).zfill(6)}.jpg"
    
    def read_frame(self, advance_pointer=True) -> Optional[Frame]:
        frame_path = self._frame_path(self._next_frame_index)
        if not frame_path.is_file():
            return None

        img = cv2.imread(frame_path)
        frame = Frame(img)

        if self.is_heterogenous:
            if frame.width != self.width or frame.height != self.height:
                raise Exception(
                    "The loaded frame does not match the stream resolution"
                )

        if advance_pointer:
            self._next_frame_index += 1
        
        return frame

    def write_frame(
        self,
        frame: Frame,
        seek_to: Optional[int] = None,
        advance_pointer=True,
    ):
        if self.is_heterogenous:
            if frame.width != self.width or frame.height != self.height:
                raise Exception(
                    "Frame resolution has to match the stream resolution"
                )
        
        if seek_to is not None:
            self.seek(seek_to)
        
        cv2.imwrite(
            self._frame_path(self._next_frame_index),
            frame.img
        )
        
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
        frame_files = glob.glob(
            pathname="frame_*.jpg",
            root_dir=self._folder_path
        )
        return len(frame_files)
