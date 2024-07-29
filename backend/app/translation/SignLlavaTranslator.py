from pathlib import Path
from ..domain.ClipsCollection import ClipsCollection
from ..domain.VideoVisualFeatures import VideoVisualFeatures
from .EmbeddingNeighborLookup import EmbeddingNeighborLookup
from .ContextTracker import ContextTracker
from .SignLlavaCache import SignLlavaCache


from llava.sign_public_api import SignLlava, SignLlavaInput, \
    SignLlavaOutput, GenerationConfig, prepare_translation_prompt


MAX_CONTEXT_LENGTH = 8_000


class SignLlavaTranslator:
    def __init__(
        self,
        clips_collection_file: Path,
        mae_features_file: Path,
        dino_features_file: Path,
        s2v_features_file: Path,
        sign_llava_cache: SignLlavaCache
    ):
        self.clips_collection_file = clips_collection_file
        self.mae_features_file = mae_features_file
        self.dino_features_file = dino_features_file
        self.s2v_features_file = s2v_features_file
        self.sign_llava_cache = sign_llava_cache

    def run(self):
        print("Loading SignLlava model...")
        sign_llava: SignLlava = self.sign_llava_cache.resolve()
        lookup = EmbeddingNeighborLookup(
            token_embeddings=sign_llava.get_embedding_layer_weights(),
            tokens=sign_llava.get_all_tokens()
        )
        context_tracker = ContextTracker(MAX_CONTEXT_LENGTH)

        # load input data
        video_features = VideoVisualFeatures.load_all(
            mae_features_file=self.mae_features_file,
            dino_features_file=self.dino_features_file,
            s2v_features_file=self.s2v_features_file
        )
        clips_collection = ClipsCollection.load(self.clips_collection_file)

        # perform translation clip-by-clip
        for clip in clips_collection.clips:
            
            # prepare data for the clip translation
            clip_features = video_features.select_clip(clip)
            context = context_tracker.get_current_context()

            # run the LLM translation
            llm_input = SignLlavaInput(
                mae_features=clip_features.mae_features,
                dino_features=clip_features.dino_features,
                sign2vec_features=clip_features.s2v_features,
                prompt=prepare_translation_prompt(context=context),
                generation_config=GenerationConfig()
            )
            llm_output: SignLlavaOutput = sign_llava.run_inference(llm_input)
            
            # store translation and its context
            clip.translation_context = context
            clip.translation_result = llm_output.output
            context_tracker.add_next_output(llm_output.output)

            # compute visual embedding neighbors
            clip.embedding_neighbor_tokens_mae = lookup.find_neighbors_for(
                llm_output.mae_embeddings
            )
            clip.embedding_neighbor_tokens_dino = lookup.find_neighbors_for(
                llm_output.dino_embeddings
            )
            clip.embedding_neighbor_tokens_s2v = lookup.find_neighbors_for(
                llm_output.sign2vec_embeddings
            )

            print(f"Clip {clip.clip_index} was translated.")
        
        # store the modified clips collection file
        clips_collection.store(self.clips_collection_file)
        print(f"The video was translated.")
