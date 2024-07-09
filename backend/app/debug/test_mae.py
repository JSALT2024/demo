import os
import sys
import torch
import numpy as np
from PIL import Image


sys.path.append("models/MAE/mae")
import models_mae


# Testing code based on:
# https://github.com/JSALT2024/MAE/blob/video_mae/notebooks/mae-predict.ipynb


def load_image(path: str):
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406])
    IMAGENET_STD = np.array([0.229, 0.224, 0.225])

    img = Image.open(path)
    img = img.resize((224, 224))
    img = np.array(img) / 255.0

    assert img.shape == (224, 224, 3)

    # normalize by ImageNet mean and std
    img = img - IMAGENET_MEAN
    img = img / IMAGENET_STD
    
    return img


def prepare_model(chkpt_dir: str, arch: str):
    # build model
    model = getattr(models_mae, arch)()
    
    # load model
    checkpoint = torch.load(chkpt_dir, map_location="cpu")
    msg = model.load_state_dict(checkpoint["model"], strict=False)
    print(msg)
    return model


def predict(model: torch.nn.Module, image: np.ndarray, mask_ratio: float = 0.75):
    # prepare input
    x = torch.tensor(image)
    x = x.unsqueeze(dim=0)
    x = torch.einsum("nhwc->nchw", x)

    # run MAE
    _, y, mask = model(x.float(), mask_ratio=mask_ratio)
    
    # unbatch, unpatchify data
    y = y.detach().cpu()
    mask = mask.detach().cpu()
    
    x = torch.einsum("nchw->nhwc", x)
    
    y = model.unpatchify(y)
    y = torch.einsum("nchw->nhwc", y)
    
    mask = mask.unsqueeze(-1).repeat(1, 1, model.patch_embed.patch_size[0]**2 *3)  # (N, H*W, p*p*3)
    mask = model.unpatchify(mask)  # 1 is removing, 0 is keeping !!!
    mask = torch.einsum("nchw->nhwc", mask)
    
    return x, y, mask


def test_mae():
    checkpoint_path = "checkpoints/MAE/mae_visualize_vit_large.pth"
    model_name = "mae_vit_large_patch16"
    image_path = "checkpoints/MAE/debug_image.jpg"

    if not os.path.exists(image_path):
        debug_image_url = "https://i.ytimg.com/vi/BhWvi5bLX8M/hqdefault.jpg"
        print("ERROR: Download the testing image first:")
        print(f"    wget {debug_image_url} -O {image_path}")
        return

    # load model
    model_mae = prepare_model(checkpoint_path, model_name)
    print("Model loaded.")

    image = load_image(image_path)
    x, y, mask = predict(model_mae, image)

    print(x, y, mask)


if __name__ == "__main__":
    test_mae()
