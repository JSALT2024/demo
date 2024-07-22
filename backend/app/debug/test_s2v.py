import torch
import numpy as np

import sys
sys.path.append("models/sign2vec")

from sign2vec.modeling_sign2vec import Sign2VecModel, Sign2VecFeatureExtractor

model = Sign2VecModel.from_pretrained(
    "karahansahin/sign2vec-yasl-sc-sc-64-8-d1",
    token=None # TODO: enter my personal hf access token
)

feature_extractor = Sign2VecFeatureExtractor()

# structure of the feature_extractor inputs
inputs = {
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
    "pose_landmarks": np.ndarray, # 33 landmarks

    # these have analogous structure
    "right_hand_landmarks": np.ndarray, # 21 landmarks
    "left_hand_landmarks": np.ndarray, # 21 landmarks
    "face_landmarks": np.ndarray, # 478 landmarks
}

features = feature_extractor(inputs) # numpy array
features = torch.tensor(features).float()
features = features.unsqueeze(0)
features = features.transpose(1, 2)
features = model(input_values=features.to("cuda:0"), output_hidden_states=True)
features = features.last_hidden_state.detach().cpu().numpy()[0]

# the structure of features:
# - it's a numpy array
# - the temporal dimensions changed because of the use of convolutions
# - the shape is [TIME, FEATURES]
# - FEATURES=768
# - TIME=(input time / 5) ... plus rounding at the edges
# - the dtype is np.float32 ??? (probbably)
