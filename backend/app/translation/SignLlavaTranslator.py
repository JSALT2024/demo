from pathlib import Path
from ..domain.ClipsCollection import ClipsCollection
from ..domain.Clip import Clip
import numpy as np
from typing import List, Optional


from llava.sign_public_api import SignLlava, SignLlavaInput, \
    SignLlavaOutput, GenerationConfig, prepare_translation_prompt


class ContextTracker:
    def __init__(self, max_length: int):
        self.max_length = max_length
        self._previous_clips: List[str] = []
        self._total_length = 0
    
    def add_next_output(self, output: str):
        self._previous_clips.append(output)
        self._total_length += len(output)
    
    def _truncate_length(self):
        while self._total_length > self.max_length:
            if len(self._previous_clips) == 0:
                return
            size_delta = len(self._previous_clips[0])
            self._previous_clips.pop(0)
            self._total_length -= size_delta

    def get_current_context(self) -> Optional[str]:
        if len(self._previous_clips) == 0:
            return None
        return " ".join(self._previous_clips)


class SignLlavaTranslator:
    def __init__(
        self,
        clips_collection_file: Path,
        embeddings_mae_file: Path,
        embeddings_s2v_file: Path,
        embeddings_dino_file: Path,
    ):
        self.clips_collection_file=clips_collection_file
        self.embeddings_mae_file=embeddings_mae_file
        self.embeddings_s2v_file=embeddings_s2v_file
        self.embeddings_dino_file=embeddings_dino_file

        self.MODEL_CHECKPOINT_FOLDER = \
            "checkpoints/Sign_LLaVA/test_ckpt_July_26_2024_11am"
        self.MAX_CONTEXT_LENGTH = 8_000
    
    def run(self):
        print("Loading SignLlava model...")
        sign_llava = SignLlava.load_from_checkpoint(
            self.MODEL_CHECKPOINT_FOLDER
        )

        # load input data
        with open(self.embeddings_s2v_file, "rb") as file:
            embeddings_s2v: dict = np.load(file) # keys are "clip_123"
            embeddings_s2v = { # keep all in memory
                k: v
                for k, v in embeddings_s2v.items()
            }
        with open(self.embeddings_mae_file, "rb") as file:
            embeddings_mae: np.ndarray = np.load(file)
        with open(self.embeddings_dino_file, "rb") as file:
            embeddings_dino: np.ndarray = np.load(file)
        clips_collection = ClipsCollection.load(self.clips_collection_file)

        # perform translation clip-by-clip
        context_tracker = ContextTracker(self.MAX_CONTEXT_LENGTH)
        for clip_index, clip in enumerate(clips_collection.clips):
            frames_from = clip.start_frame
            frames_to = clip.start_frame + clip.frame_count
            context = context_tracker.get_current_context()
            clip_data = SignLlavaInput(
                sign2vec_features=embeddings_s2v[f"clip_{clip_index}"],
                mae_features=embeddings_mae[frames_from:frames_to, :],
                dino_features=embeddings_dino[frames_from:frames_to, :],
                prompt=prepare_translation_prompt(context=context),
                generation_config=GenerationConfig()
            )
            output_data: SignLlavaOutput = sign_llava.run_inference(clip_data)
            
            clip.translation_context = context
            clip.translation_result = output_data.output

            context_tracker.add_next_output(output_data.output)

            print(
                f"Clip {clip_index} was translated as:",
                repr(output_data.output)
            )
        
        # store the modified clips collection file
        clips_collection.store(self.clips_collection_file)
        print(f"The video was translated.")
