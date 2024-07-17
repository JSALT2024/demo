from ..preprocessing.FileFrameStream import FileFrameStream
from ..preprocessing.InMemoryFrameStream import InMemoryFrameStream
from ..preprocessing.ClipSplitter import ClipSplitter
from pathlib import Path
import sys


sys.path.append("models/PoseEstimation")
from predict_pose import predict_pose, create_mediapipe_models


def test_mediapipe(video_file_path: Path):
    frame_stream = FileFrameStream(video_file_path)

    # splitter = ClipSplitter(frame_stream, target_clip_length_seconds=1)
    # for i, clip in enumerate(splitter):
    #     clip.dump_npz(video_file_path.parent / f"clip_{str(i).zfill(6)}.npz")

    models = create_mediapipe_models("checkpoints/PoseEstimation")
    video = [frame.img for frame in frame_stream]
    prediction = predict_pose(video, models)

    print(prediction)


if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    files_repo = app.video_folder_repository_factory.get_repository(video.id)
    test_mediapipe(files_repo.to_global_path(video.normalized_file.file_path))
