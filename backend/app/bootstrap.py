import logging
from .Application import Application
from pathlib import Path
from dotenv import load_dotenv


def bootstrap() -> Application:
    """Creates the application instance"""
    
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
