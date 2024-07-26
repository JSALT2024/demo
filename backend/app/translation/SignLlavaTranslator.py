from pathlib import Path
from ..domain.ClipsCollection import ClipsCollection
from ..domain.Clip import Clip
import numpy as np


from llava.sign_public_api import SignLlava, SignLlavaInput, \
    SignLlavaOutput, GenerationConfig, prepare_translation_prompt


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
        context = None
        for clip_index, clip in enumerate(clips_collection.clips):
            frames_from = clip.start_frame
            frames_to = clip.start_frame + clip.frame_count
            clip_data = SignLlavaInput(
                sign2vec_features=embeddings_s2v[f"clip_{clip_index}"],
                mae_features=embeddings_mae[frames_from:frames_to, :],
                dino_features=embeddings_dino[frames_from:frames_to, :],
                prompt=prepare_translation_prompt(
                    context=context
                ),
                generation_config=GenerationConfig()
            )
            output_data: SignLlavaOutput = sign_llava.run_inference(clip_data)
            
            clip.translation_context = context
            clip.translation_result = output_data.output

            # update context
            if context is None:
                context = ""
            context += output_data.output
            context = context[-self.MAX_CONTEXT_LENGTH:]
            if len(context) == self.MAX_CONTEXT_LENGTH:
                context = "..." + context

            print(
                f"Clip {clip_index} was translated as:",
                repr(output_data.output)
            )
        
        # store the modified clips collection file
        clips_collection.store(self.clips_collection_file)
        print(f"The video was translated.")
