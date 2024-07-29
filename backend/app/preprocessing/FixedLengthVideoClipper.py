from ..domain.ClipsCollection import ClipsCollection
from ..domain.Clip import Clip
from ..video.FileFrameStream import FileFrameStream
from ..video.FrameStreamChunker import FrameStreamChunker
from pathlib import Path


class FixedLengthVideoClipper:
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
        chunker = FrameStreamChunker(file_stream, self.clip_length_seconds)
        clips_collection = ClipsCollection()
        
        clip_starting_frame = 0
        clip_index = 0
        for clip_frames in chunker:
            clip_frame_count = len(clip_frames)
            
            clip = Clip(
                clip_index=clip_index,
                start_frame=clip_starting_frame,
                frame_count=clip_frame_count
            )
            clips_collection.clips.append(clip)

            clip_starting_frame += clip_frame_count
            clip_index += 1

        clips_collection.recompute_lookup_table()

        return clips_collection
