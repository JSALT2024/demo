import torch
import numpy as np
import os
import sys
from dotenv import load_dotenv
load_dotenv()

sys.path.append("models/sign2vec")
from sign2vec.modeling_sign2vec import Sign2VecModel
from sign2vec.feature_extraction_sign2vec import Sign2VecFeatureExtractor


def test_s2v():
    print("Loading the S2V model...")
    model = Sign2VecModel.from_pretrained(
        "karahansahin/sign2vec-yasl-mc-sc-64-2-d1-decay",
        token=os.environ.get("HUGGINGFACE_TOKEN")
    )
    feature_extractor = Sign2VecFeatureExtractor()

    # structure of the feature_extractor inputs
    frame_count = 125
    sample_pose = {
        # shape: [TIME, LANDMARKS, (X,Y,Z,vis)]
        # with zeros where the pose was not detected
        # the temporal:
        #   s2v uses max 30s, with 25 FPS, which is 750 frames
        #   the temporal length can be varied but they all need to be the same
        # the input values are np.float64
        # the temporal size influences the RAM usage, the limit is precisely here
        # because of RAM, because the attention matrix of the tranformer layers
        # become too large, so let's slice into 10s chunks for now
        # - the sign2vec model uses only the first two feature dimensions (X, Y)
        #   of the input data, so the number and meaning of the remaining ones
        #   does not matter.
        "pose_landmarks": np.zeros(shape=(frame_count, 33, 4), dtype=np.float64),

        # these have analogous structure
        "right_hand_landmarks": np.zeros(shape=(frame_count, 21, 4), dtype=np.float64),
        "left_hand_landmarks": np.zeros(shape=(frame_count, 21, 4), dtype=np.float64),
        "face_landmarks": np.zeros(shape=(frame_count, 478, 4), dtype=np.float64),
    }

    print("Running the S2V model...")
    inputs = feature_extractor(sample_pose)
    features = inputs["input_values"][0]
    features = torch.tensor(features).float()
    features = features.transpose(1, 2)
    out = model(features)
    sign2vec_features = out.last_hidden_state.detach().cpu().numpy()[0]

    # the structure of features:
    # - it's a numpy array
    # - the temporal dimensions changed because of the use of convolutions
    # - the shape is [TIME, FEATURES]
    # - FEATURES=768
    # - TIME=(input time / 2) ... plus rounding at the edges
    # - the dtype is np.float32

    assert type(sign2vec_features) is np.ndarray
    assert len(sign2vec_features.shape) == 2
    assert sign2vec_features.shape[0] <= frame_count
    assert sign2vec_features.shape[1] == 768
    assert str(sign2vec_features.dtype) == "float32"

    print("SIGN2VEC returns sensible results.")


if __name__ == "__main__":
    test_s2v()
