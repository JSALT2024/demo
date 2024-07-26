import sys
import torch
import numpy as np


sys.path.append("models/DINOv2/predict")
import predict_dino


def test_dino():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    face_checkpoint = "checkpoints/DINOv2/face_dinov2_vits14_reg_teacher_checkpoint.pth"
    hand_checkpoint = "checkpoints/DINOv2/hand_dinov2_vits14_reg_teacher_checkpoint.pth"

    print("Loading the DINO models...")
    face_model = predict_dino.create_dino_model(face_checkpoint)
    hand_model = predict_dino.create_dino_model(hand_checkpoint)
    face_model.to(device)
    hand_model.to(device)

    print("Running the DINO models...")
    dummy_image = np.zeros(shape=(56, 56, 3), dtype=np.uint8)
    face_features = predict_dino.dino_predict(
        [dummy_image] * 5, face_model, predict_dino.transform_dino, device
    )
    left_features = predict_dino.dino_predict(
        [dummy_image] * 5, hand_model, predict_dino.transform_dino, device
    )
    right_features = predict_dino.dino_predict(
        [dummy_image] * 5, hand_model, predict_dino.transform_dino, device
    )
    features = np.concatenate([face_features, left_features, right_features], 1)

    assert type(features) is np.ndarray
    assert features.shape == (5, 1152)

    print("DINO returns sensible results.")


if __name__ == "__main__":
    test_dino()
