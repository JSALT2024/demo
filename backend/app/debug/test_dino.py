import sys
import cv2
import torch
import numpy as np


sys.path.append("models/DINOv2/predict")
import predict_dino


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

face_checkpoint = "checkpoints/DINOv2/face_dinov2_vits14_reg_teacher_checkpoint.pth"
hand_checkpoint = "checkpoints/DINOv2/hand_dinov2_vits14_reg_teacher_checkpoint.pth"
face_image_path = "checkpoints/DINOv2/test_face.jpg"
left_image_path = "checkpoints/DINOv2/test_left_hand.jpg"
right_image_path = "checkpoints/DINOv2/test_right_hand.jpg"

face_model = predict_dino.create_dino_model(face_checkpoint)
hand_model = predict_dino.create_dino_model(hand_checkpoint)
face_model.to(device)
hand_model.to(device)

face_image = cv2.imread(face_image_path)
left_hand_image = cv2.imread(left_image_path)
right_hand_image = cv2.imread(right_image_path)

face_features = predict_dino.dino_predict(
    [face_image] * 5, face_model, predict_dino.transform_dino, device
)
left_features = predict_dino.dino_predict(
    [left_hand_image] * 5, hand_model, predict_dino.transform_dino, device
)
right_features = predict_dino.dino_predict(
    [right_hand_image] * 5, hand_model, predict_dino.transform_dino, device
)
features = np.concatenate([face_features, left_features, right_features], 1)

print(features.shape)
