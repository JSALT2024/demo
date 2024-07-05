from pathlib import Path
import cv2


def process_video(video_file_path: Path):
    vidcap = cv2.VideoCapture(str(video_file_path))
    frame_index = -1

    frames_dir = video_file_path.parent / "frames"
    frames_dir.mkdir(exist_ok=True)

    while True:
        success, frame = vidcap.read()
        frame_index += 1
        if not success:
            break

        # work with the frame!
        print(frame_index, frame.shape)
        cv2.imwrite(
            str(frames_dir / f"frame_{str(frame_index).zfill(4)}.jpg"),
            frame
        )
    
    vidcap.release()


# DEBUGGING
if __name__ == "__main__":
    from ..bootstrap import bootstrap
    app = bootstrap()
    video = app.videos_repository.all()[0]
    files_repo = app.video_files_repository_factory.get_repository(video.id)
    process_video(files_repo.video_file_path)
