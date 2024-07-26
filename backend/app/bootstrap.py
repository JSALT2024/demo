import logging
from .Application import Application
from pathlib import Path
from dotenv import load_dotenv
from .add_venv_bin_to_path import add_venv_bin_to_path
import torch


def bootstrap() -> Application:
    """Creates the application instance"""

    if torch.cuda.is_available():
        print("Detecting devices... running torch on CUDA.")
    else:
        print("Detecting devices... running torch on CPU.")
    
    # extend $PATH to include .venv/bin
    # (so that ffmpeg and ffprobe work)
    add_venv_bin_to_path()

    # environment variables
    load_dotenv()

    # logging
    logging.basicConfig(level=logging.INFO)

    # storage
    storage_path = Path("storage")

    # create the instance    
    return Application(
        storage_folder=storage_path
    )
