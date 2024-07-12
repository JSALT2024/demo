from dataclasses import dataclass
from pathlib import Path
import mimetypes
import cv2
import logging


@dataclass
class VideoFile:
    """
    Represents a video file existing somewhere in the backend file system.
    """
    
    media_type: str
    "MIME type of the video"

    file_path: Path
    "Path to the file relative to some parent folder, depending on the usecase"

    duration_seconds: float
    "Length of the video in seconds"
    
    frame_count: int
    "Number of frames in the video"

    framerate: float
    "Frames per second of the video"

    frame_width: int
    "With of each frame in pixels"

    frame_height: int
    "Height of each frame in pixels"

    file_size_bytes: int
    "Size of the video file in bytes"

    @staticmethod
    def from_existing_file(root_path: Path, file_path: Path) -> "VideoFile":
        """Extracts metadata from an existing file"""

        media_type, _ = mimetypes.guess_type(file_path.name)
        if media_type is None:
            raise Exception(
                "Cannot get MIME type for filename " + file_path.name
            )
        
        capture = cv2.VideoCapture(file_path)
        frame_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        framerate = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # count frames if the header does not exist
        if frame_count <= 0:
            logging.warning(
                f"File {file_path} lacks frame count metadata, " +\
                "counting frames instead..."
            )
            frame_count = 0
            while True:
                success, _ = capture.read()
                if not success:
                    break
                frame_count += 1
        
        duration_seconds = float(frame_count / framerate)
        
        capture.release()
        
        return VideoFile(
            media_type=media_type,
            file_path=file_path.relative_to(root_path),
            duration_seconds=duration_seconds,
            frame_count=frame_count,
            framerate=framerate,
            frame_width=frame_width,
            frame_height=frame_height,
            file_size_bytes=file_path.stat().st_size
        )
