import numpy as np


class Frame:
    """
    Represents a single video frame

    The frame is stored as a numpy array of shape [height, width, BGR]
    with the three channels in the OpenCV BGR format. The array contains uint8
    values in the range 0 - 255.
    """
    def __init__(self, img: np.ndarray):
        assert len(img.shape) == 3
        assert str(img.dtype) == "uint8"
        self.img = img

    @property
    def width(self) -> int:
        """Width of the frame image in pixels"""
        return self.img.shape[1]
    
    @property
    def height(self) -> int:
        """Height of the frame image in pixels"""
        return self.img.shape[0]
    
    @property
    def bytes_size(self) -> int:
        """Size of the frame in memory in bytes"""
        return self.width * self.height * 3
    
    def __repr__(self) -> str:
        return f"Frame({self.width}x{self.height})"
