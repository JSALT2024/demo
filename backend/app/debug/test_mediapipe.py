from ..preprocessing.FileFrameStream import FileFrameStream
from ..preprocessing.InMemoryFrameStream import InMemoryFrameStream
from ..preprocessing.ClipSplitter import ClipSplitter
from pathlib import Path


def test_mediapipe(video_file_path: Path):
    frame_stream = FileFrameStream(video_file_path)

    splitter = ClipSplitter(frame_stream, target_clip_length_seconds=1)

    for i, clip in enumerate(splitter):
        clip.dump_npz(video_file_path.parent / f"clip_{str(i).zfill(6)}.npz")

    print("DONE")


if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    files_repo = app.video_files_repository_factory.get_repository(video.id)
    test_mediapipe(files_repo.video_file_path)
