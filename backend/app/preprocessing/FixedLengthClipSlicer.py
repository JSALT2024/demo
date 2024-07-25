from ..domain.ClipsCollection import ClipsCollection
from ..domain.Clip import Clip
from .FileFrameStream import FileFrameStream
from .ClipSplitter import ClipSplitter
from pathlib import Path


class FixedLengthClipSlicer:
    """
    Creates the clips collection datastructure for a video, i.e. defines the
    clips to be used during translation.
    """

    def __init__(
        self,
        normalized_video_file: Path,
        clip_length_seconds: float
    ):
        self.normalized_video_file = normalized_video_file
        self.clip_length_seconds = clip_length_seconds

    def run(self) -> ClipsCollection:
        file_stream = FileFrameStream(self.normalized_video_file)
        splitter = ClipSplitter(file_stream, self.clip_length_seconds)
        clips_collection = ClipsCollection()
        
        clip_starting_frame = 0
        for clip_frames in splitter:
            clip_frame_count = len(clip_frames)
            
            clip = Clip(
                start_frame=clip_starting_frame,
                frame_count=clip_frame_count
            )
            clips_collection.clips.append(clip)

            clip_starting_frame += clip_frame_count

        clips_collection.recompute_lookup_table()

        return clips_collection
