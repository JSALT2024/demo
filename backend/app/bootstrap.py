import logging
from .Application import Application
from pathlib import Path


def bootstrap() -> Application:
    """Creates the application instance"""
    
    # logging
    logging.basicConfig(level=logging.INFO)

    # storage
    storage_path = Path("storage")

    # create the instance    
    return Application(
        storage_folder=storage_path
    )
