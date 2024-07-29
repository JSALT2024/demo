from ..translation.SignLlavaCache import SignLlavaCache
from .VideoFolderRepository import VideoFolderRepository
from ..domain.VideoVisualFeatures import VideoVisualFeatures
from ..domain.Clip import Clip


from llava.sign_public_api import SignLlava, SignLlavaInput, \
    SignLlavaOutput, GenerationConfig


def retranslate_clip(
    use_mae: bool,
    use_dino: bool,
    use_sign2vec: bool,
    prompt: str,
    clip: Clip,
    video_folder: VideoFolderRepository,
    sign_llava_cache: SignLlavaCache,
) -> str:
    """Runs the LLM on a video clip again to get a different response"""
    
    sign_llava: SignLlava = sign_llava_cache.resolve()

    # load input data
    video_features = VideoVisualFeatures.load_all(
        mae_features_file=video_folder.MAE_FEATURES_FILE,
        dino_features_file=video_folder.DINO_FEATURES_FILE,
        s2v_features_file=video_folder.S2V_FEATURES_FILE
    )
    clip_features = video_features.select_clip(clip)

    # throw away disabled visual features
    if not use_mae:
        clip_features.mae_features = None
    if not use_dino:
        clip_features.dino_features = None
    if not use_sign2vec:
        clip_features.s2v_features = None

    # run the LLM translation for the clip
    llm_input = SignLlavaInput(
        mae_features=clip_features.mae_features,
        dino_features=clip_features.dino_features,
        sign2vec_features=clip_features.s2v_features,
        prompt=prompt,
        generation_config=GenerationConfig()
    )
    llm_output: SignLlavaOutput = sign_llava.run_inference(llm_input)
    
    return llm_output.output
