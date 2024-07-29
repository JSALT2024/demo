from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Clip:
    """
    Contains data about a clip of a video
    """

    clip_index: int
    "Index of this clip within the video"

    start_frame: int
    "Index of the first frame in this clip"

    frame_count: int
    "Number of frames in this clip"

    translation_context: Optional[str] = None
    "Holds the context string for the translation of this clip"

    translation_result: Optional[str] = None
    "Text obtained from the translation of this clip"

    embedding_neighbor_tokens_mae: Optional[List[str]] = None
    "For each projected embedding, contains the closest textual token"
    
    embedding_neighbor_tokens_dino: Optional[List[str]] = None
    "For each projected embedding, contains the closest textual token"

    embedding_neighbor_tokens_s2v: Optional[List[str]] = None
    "For each projected embedding, contains the closest textual token"

    @property
    def end_frame(self) -> int:
        """Index of the first frame after the last frame in the clip"""
        return self.start_frame + self.frame_count
    
    @property
    def frame_range(self) -> range:
        """Range object that can be used to select clip frames in video"""
        return range(self.start_frame, self.end_frame)

    def to_json(self) -> dict:
        return {
            "clip_index": self.clip_index,
            "start_frame": self.start_frame,
            "frame_count": self.frame_count,
            "translation_context": self.translation_context,
            "translation_result": self.translation_result,
            "embedding_neighbor_tokens_mae": self.embedding_neighbor_tokens_mae,
            "embedding_neighbor_tokens_dino": self.embedding_neighbor_tokens_dino,
            "embedding_neighbor_tokens_s2v": self.embedding_neighbor_tokens_s2v,
        }
    
    @staticmethod
    def from_json(json: dict) -> "Clip":
        def decode_neighbor(kind: str):
            nonlocal json
            key = "embedding_neighbor_tokens_" + kind
            value = json.get(key)
            if value is None:
                return None
            return [str(n) for n in value]
        
        return Clip(
            clip_index=int(json["clip_index"]),
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
            embedding_neighbor_tokens_mae=decode_neighbor("mae"),
            embedding_neighbor_tokens_dino=decode_neighbor("dino"),
            embedding_neighbor_tokens_s2v=decode_neighbor("s2v"),
        )
