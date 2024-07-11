from .FrameStream import FrameStream
from .Frame import Frame
from typing import Optional
from pathlib import Path
import cv2


class FileFrameStream(FrameStream):
    """Represents a frame stream of frames comming from a video file"""
    def __init__(self, file_path: Path):
        super().__init__()
        
        self.file_path = file_path
        "Path to the video file being read"

        self.video_capture: Optional[cv2.VideoCapture] = None
        "Open CV video capture instance"

        self.reset()
    
    def reset(self):
        """Jumps to the beginning of the file and opens it up"""
        self.close()
        self.video_capture = cv2.VideoCapture(self.file_path)

    def _assert_file_open(self):
        if self.video_capture is None:
            raise Exception("No video file open.")
    
    @property
    def framerate(self) -> float:
        self._assert_file_open()
        return self.video_capture.get(cv2.CAP_PROP_FPS)
    
    @property
    def width(self) -> int:
        self._assert_file_open()
        return int(self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    
    @property
    def height(self) -> int:
        self._assert_file_open()
        return int(self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def close(self):
        """Closes the file if open"""
        if self.video_capture is None:
            return
        
        self.video_capture.release()
        self.video_capture = None

    def __next__(self) -> Frame:
        if self.video_capture is None:
            raise Exception("No video file open.")

        success, img = self.video_capture.read()

        if not success:
            raise StopIteration

        return Frame(img)
