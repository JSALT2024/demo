import sys
import cv2
import os
import torch

sys.path.append("models/MAE/mae")
import predict_mae

# Testing code based on:
# https://github.com/JSALT2024/MAE/tree/video_mae?tab=readme-ov-file#predict-embedding

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

arch = "vit_base_patch16"
checkpoint_path = "checkpoints/MAE/vit_base_16_16-07_21-52-12_checkpoint-440.pth"
image_path = "checkpoints/MAE/debug_image.jpg"

if not os.path.exists(image_path):
    debug_image_url = "https://i.ytimg.com/vi/BhWvi5bLX8M/hqdefault.jpg"
    print("ERROR: Download the testing image first:")
    print(f"    wget {debug_image_url} -O {image_path}")
    exit()

model = predict_mae.create_mae_model(arch, checkpoint_path)
model = model.to(device)

image = cv2.imread(image_path)
mae_embedding = predict_mae.mae_predict(
    [image, image, image, image],
    model,
    predict_mae.transform_mae,
    device
)

print("Shape of the given embeddings vector list:")
print(mae_embedding.shape)
