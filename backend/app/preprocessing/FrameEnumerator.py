import ffmpeg
import cv2
import numpy as np

class FrameEnumerator:
    """Writes a frame number to the left top corner of each frame into the video frame"""
    def __init__(self, input_video_path, output_video_path, write_frame_number=False):
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        self.write_frame_number = write_frame_number
        self.frame_counter = 0

        self.probe = ffmpeg.probe(self.input_video_path)
        video_stream = next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'video'), None)
        
        self.original_fps = eval(video_stream['r_frame_rate'])
        self.frame_width = int(video_stream['width'])
        self.frame_height = int(video_stream['height'])

    def process_video(self):
        """Copies video frames"""
        process = (
            ffmpeg
            .input(self.input_video_path, r=self.original_fps)
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True)
        )

        frame_size = self.frame_width * self.frame_height * 3
        while True:
            in_bytes = process.stdout.read(frame_size)
            if len(in_bytes) != frame_size:
                break

            self._write_frame_to_output(in_bytes)

        process.stdout.close()
        process.wait()
        self.close_output()

    def _write_frame_to_output(self, frame_bytes):
        """Writes frames to the output file"""
        frame = np.frombuffer(frame_bytes, np.uint8).reshape((self.frame_height, self.frame_width, 3))

        if self.write_frame_number:
            frame = self._add_frame_number(frame)
        
        frame_bytes = frame.tobytes()

        if not hasattr(self, 'out'):
            self.out = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(self.frame_width, self.frame_height), r=self.original_fps)
            self.out = ffmpeg.output(self.out, self.output_video_path, pix_fmt='yuv420p', vcodec='libx264', r=self.original_fps)
            self.out = self.out.overwrite_output().run_async(pipe_stdin=True)

        self.out.stdin.write(frame_bytes)
        self.frame_counter += 1

    def _add_frame_number(self, frame):
        """Adds the frame number to the top-left corner of the frame"""
        text = f"{self.frame_counter}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        text_color = (255, 255, 255)
        thickness = 1
        position = (5, 13)
        
        writable_frame = frame.copy()

        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_w, text_h = text_size

        top_left = (position[0] - 5, position[1] - text_h - 5)
        bottom_right = (position[0] + text_w + 5, position[1] + 5)

        cv2.rectangle(writable_frame, top_left, bottom_right, (0, 0, 0), cv2.FILLED)
        cv2.putText(writable_frame, text, position, font, font_scale, text_color, thickness, cv2.LINE_AA)
        return writable_frame

    def close_output(self):
        """Closes the output stream"""
        if hasattr(self, 'out'):
            self.out.stdin.close()
            self.out.wait()

if __name__ == "__main__":
    input_video_path = 'VideoNormalizer/webm_test_norm.mp4'
    output_video_path = 'VideoNormalizer/webm_test_norm_NO.mp4'
    video_loader = FrameEnumerator(input_video_path, output_video_path, write_frame_number=True)
    video_loader.process_video()
