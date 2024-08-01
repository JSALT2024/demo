from typing import Optional


from llava.sign_public_api import SignLlava


SIGN_LLAVA_CHECKPOINT = "checkpoints/Sign_LLaVA"


class SignLlavaCache:
    """
    Holds a loaded instance of the LLM so that it can be used immediately by
    various jobs without loading it each time. Because the loading takes
    cca 10 seconds and re-translation is therefore quite lazy otherwise.

    This class is also responsible for loading the Sign LLaVA model onto GPU.
    """
    def __init__(self):
        self._model: Optional[SignLlava] = None

    def resolve(self) -> SignLlava:
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self):
        self._model = SignLlava.load_from_checkpoint(SIGN_LLAVA_CHECKPOINT)
    