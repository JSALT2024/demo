from .Frame import Frame
import abc


class FrameStream(abc.ABC):
    """Represents a stream of video frames"""
    @property
    @abc.abstractmethod
    def framerate(self) -> float:
        """Returns the FPS of the frame stream"""
        raise NotImplementedError
    
    @property
    @abc.abstractmethod
    def width(self) -> float:
        """Width of frames in the stream"""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def height(self) -> float:
        """Height of frames in the stream"""
        raise NotImplementedError
    
    def __iter__(self):
        return self
    
    @abc.abstractmethod
    def __next__(self) -> Frame:
        raise NotImplementedError
