from .FrameStream import FrameStream
from .InMemoryFrameStream import InMemoryFrameStream
from typing import Optional


class ClipSplitter:
    """Chunks up a frame stream into video clips"""
    def __init__(
        self,
        in_stream: FrameStream,
        target_clip_length_seconds=10.0,
    ):
        self.in_stream = in_stream
        "The input stream of frames"

        self.target_clip_length_seconds = target_clip_length_seconds
        "The maximum length of the clip in seconds"

        self.target_clip_frame_count = int(
            self.target_clip_length_seconds * self.in_stream.framerate
        )
        "The maximum length of the clip in frames"
    
    def get_next_clip(self) -> Optional[InMemoryFrameStream]:
        """Slices off a new clip from the input frame stream"""
        out_stream = InMemoryFrameStream(
            framerate=self.in_stream.framerate,
            width=self.in_stream.width,
            height=self.in_stream.height
        )

        for _ in range(self.target_clip_frame_count):
            try:
                frame = next(self.in_stream)
            except StopIteration:
                break
            out_stream.write_frame(frame)
        
        if len(out_stream) == 0:
            return None
        
        return out_stream
    
    def __iter__(self):
        return self
    
    def __next__(self) -> InMemoryFrameStream:
        out_stream = self.get_next_clip()
        
        if out_stream is None:
            raise StopIteration
        
        return out_stream
