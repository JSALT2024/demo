from dataclasses import dataclass
from typing import Optional


@dataclass
class Clip:
    """
    Contains data about a clip of a video
    """

    start_frame: int
    "Index of the first frame in this clip"

    frame_count: int
    "Number of frames in this clip"

    translation_context: Optional[str] = None
    "Holds the context string for the translation of this clip"

    translation_result: Optional[str] = None
    "Text obtained from the translation of this clip"

    def to_json(self) -> dict:
        return {
            "start_frame": self.start_frame,
            "frame_count": self.frame_count,
            "translation_context": self.translation_context,
            "translation_result": self.translation_result
        }
    
    @staticmethod
    def from_json(json: dict) -> "Clip":
        return Clip(
            start_frame=int(json["start_frame"]),
            frame_count=int(json["frame_count"]),
            translation_context=(
                None if json["translation_context"] is None
                else str(json["translation_context"])
            ),
            translation_result=(
                None if json["translation_result"] is None
                else str(json["translation_result"])
            ),
        )
