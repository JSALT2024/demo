from pathlib import Path


class VideoFolderRepository:
    """
    Encapsulates access to files that describe a single uploaded video
    (the video itself, its frames, metadata and translation results)
    This repository assumes the video is stored in the local file system
    in a single folder.
    """
    def __init__(self, video_id: str, video_folder: Path):
        self.video_id = video_id
        self._video_folder = video_folder

        # define common file paths
        self.LOG_FILE = self.path("log.txt")
        self.NORMALIZED_FILE = self.path("normalized_file.mp4") # always mp4
        self.GEOMETRY_FILE = self.path("geometry.json")
        self.CROPPED_LEFT_HAND_FOLDER = self.path("cropped_left_hand")
        self.CROPPED_RIGHT_HAND_FOLDER = self.path("cropped_right_hand")
        self.CROPPED_FACE_FOLDER = self.path("cropped_face")
        self.CROPPED_IMAGES_FOLDER = self.path("cropped_images")
        self.CLIPS_COLLECTION_FILE = self.path("clips_collection.json")
        self.MAE_FEATURES_FILE = self.path("mae_features.npy")
        self.S2V_FEATURES_FILE = self.path("s2v_features.npz")
        self.DINO_FEATURES_FILE = self.path("dino_features.npy")

    def path(self, repository_local_path: Path) -> Path:
        """Converts repo-local path to an actual, usable path"""
        return self._video_folder / repository_local_path
    
    @property
    def root_path(self) -> Path:
        """Path to the folder representing this video repository"""
        return self._video_folder
