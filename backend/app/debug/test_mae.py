import sys
import torch
import numpy as np


sys.path.append("models/MAE/mae")
import predict_mae


def test_mae():
    # Testing code based on:
    # https://github.com/JSALT2024/MAE/tree/video_mae?tab=readme-ov-file#predict-embedding
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    arch = "vit_base_patch16"
    checkpoint_path = "checkpoints/MAE/vit_base_16_16-07_21-52-12_checkpoint-440.pth"

    print("Loading the MAE model...")
    model = predict_mae.create_mae_model(arch, checkpoint_path)
    model = model.to(device)

    print("Running the MAE model...")
    image = np.zeros(shape=(1920, 1080, 3), dtype=np.uint8)
    mae_embedding = predict_mae.mae_predict(
        [image, image, image, image],
        model,
        predict_mae.transform_mae,
        device
    )

    assert type(mae_embedding) is np.ndarray
    assert mae_embedding.shape == (4, 768)

    print("MAE returns sensible results.")


if __name__ == "__main__":
    test_mae()
