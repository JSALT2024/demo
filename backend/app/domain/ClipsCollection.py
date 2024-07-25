from dataclasses import dataclass, field
from typing import List, Optional
from .Clip import Clip
import json
from pathlib import Path


@dataclass
class ClipsCollection:
    """Contains information about all the clips in a video"""

    clips: List[Clip] = field(default_factory=lambda: [])
    "List of all clips ordered by their index"

    clip_index_lookup: List[int] = field(default_factory=lambda: [])
    "Mapping from frame index to clip index"
    
    def clip_index_for_frame(self, frame_index: int) -> int:
        return self.clip_index_lookup[frame_index]

    def recompute_lookup_table(self):
        lookup = []
        for clip_index, clip in enumerate(self.clips):
            assert clip.start_frame == len(lookup), "Clips don't meet properly"
            lookup += [clip_index] * clip.frame_count
        self.clip_index_lookup = lookup

    def to_json(self) -> dict:
        return {
            "clips": [clip.to_json() for clip in self.clips],
            "clip_index_lookup": self.clip_index_lookup
        }
    
    @staticmethod
    def from_json(json_data: dict) -> "ClipsCollection":
        return ClipsCollection(
            clips=[Clip.from_json(clip) for clip in json_data["clips"]],
            clip_index_lookup=json_data["clip_index_lookup"]
        )
    
    def store(self, file: Path):
        with open(file, "w") as f:
            json_data = self.to_json()
            json.dump(json_data, f)

    @staticmethod
    def load(file: Path) -> "ClipsCollection":
        with open(file, "r") as f:
            json_data = json.load(f)
            return ClipsCollection.from_json(json_data)
