import time


def retranslate_clip(
    use_mae: bool,
    use_dino: bool,
    use_sign2vec: bool,
    prompt: str
) -> str:
    """Runs the LLM on a video clip again to get a different response"""
    
    # TODO: get the loaded model (cache model loading)
    # TODO: load visual features
    # TODO: run translation for one clip
    
    time.sleep(2.0) # simulate workload
    return "Hello world!"
