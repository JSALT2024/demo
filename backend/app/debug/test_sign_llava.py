from llava.sign_public_api import SignLlava, SignLlavaInput, \
    SignLlavaOutput, GenerationConfig, prepare_translation_prompt
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv() # because of huggingface token


def test_sign_llava():
    print("Loading the Sign LLaVA model...")
    our_model = SignLlava.load_from_checkpoint(
        "checkpoints/Sign_LLaVA/test_ckpt_July_26_2024_11am"
    )

    input_data = SignLlavaInput(
        sign2vec_features=np.zeros(shape=(150, 768), dtype=np.float32),
        mae_features=np.zeros(shape=(300, 768), dtype=np.float32),
        dino_features=np.zeros(shape=(300, 1152), dtype=np.float32),
        prompt=prepare_translation_prompt(context=None),
        generation_config=GenerationConfig()
    )
    output_data: SignLlavaOutput = our_model.run_inference(input_data)

    print("The LLM says:", repr(output_data.output))
    assert len(output_data.mae_embeddings.shape) == 2
    assert output_data.mae_embeddings.shape[0] == 300

    print("The result form the LLM seems ok.")


if __name__ == "__main__":
    test_sign_llava()
