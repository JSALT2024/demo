import os
import math
import ffmpeg
import warnings

class VideoNormalizer:
    """Normalizes fps and resolution of demo input video"""
    def __init__(self, input_video_path, output_video_path, target_fps=30, target_size=1280, fps_lower_bound = 24, fps_higher_bound = 30):
        self.target_size = target_size
        self.input_video_path = input_video_path
        self.output_video_path = output_video_path
        self.target_fps = target_fps
        self.fps_lower_bound = fps_lower_bound
        self.fps_higher_bound = fps_higher_bound

        if not os.path.exists(self.input_video_path):
            raise FileNotFoundError(f"Input video file '{self.input_video_path}' does not exist.")

        try:
            self.probe = ffmpeg.probe(self.input_video_path)
        except ffmpeg.Error as e:
            raise RuntimeError(f"Error probing input video file '{self.input_video_path}': {e}")

        video_stream = next((stream for stream in self.probe['streams'] if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            raise ValueError("Error: Could not find video stream in input video.")
        
        try:
            self.original_fps = eval(video_stream['r_frame_rate'])
        except (SyntaxError, NameError):
            raise ValueError(f"Error: Invalid frame rate '{video_stream['r_frame_rate']}' in input video.")

        self.frame_width = int(video_stream['width'])
        self.frame_height = int(video_stream['height'])
        self.total_frames = int(video_stream.get('nb_frames', 0))
        if self.total_frames == 0:
            warnings.warn("Warning: Total frames count is zero or not available in the input video.")

    def process_video(self):
        """Defines what to do with the input video"""
        try:
            if self.original_fps >= self.fps_lower_bound and self.original_fps <= self.fps_higher_bound:
                self._copy_frames()
            elif self.original_fps > self.target_fps:
                self._reduce_fps()
            else:
                self._increase_fps()
        except Exception as e:
            raise RuntimeError(f"Error processing video: {e}")
    
    def _copy_frames(self):
        """Copies video frames in case of keeping the frame rate"""
        try:
            process = (
                ffmpeg
                .input(self.input_video_path)
                .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                .run_async(pipe_stdout=True)
            )

            frame_size = self.frame_width * self.frame_height * 3
            while True:
                in_bytes = process.stdout.read(frame_size)
                if not in_bytes:
                    break

                self._write_frame_to_output(in_bytes, self.original_fps)

            process.wait()
        except ffmpeg.Error as e:
            raise RuntimeError(f"ffmpeg error while copying frames: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in _copy_frames: {e}")

    def _reduce_fps(self):
        """Reduces the frame rate"""
        try:
            process = (
                ffmpeg
                .input(self.input_video_path)
                .filter('fps', fps=self.target_fps, round='down')
                .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                .global_args('-loglevel', 'quiet')  # Suppress ffmpeg console output
                .run_async(pipe_stdout=True)
            )

            frame_size = self.frame_width * self.frame_height * 3
            while True:
                in_bytes = process.stdout.read(frame_size)
                if not in_bytes:
                    break

                self._write_frame_to_output(in_bytes, self.target_fps)

            process.wait()
        except ffmpeg.Error as e:
            raise RuntimeError(f"ffmpeg error while reducing fps: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in _reduce_fps: {e}")

    def _increase_fps(self):
        """Increases the frame rate"""
        try:
            process = (
                ffmpeg
                .input(self.input_video_path)
                .filter('fps', fps=self.target_fps, round='down')
                .output('pipe:', format='rawvideo', pix_fmt='rgb24')
                .global_args('-loglevel', 'quiet')  # Suppress ffmpeg console output
                .run_async(pipe_stdout=True)
            )

            frame_size = self.frame_width * self.frame_height * 3
            while True:
                in_bytes = process.stdout.read(frame_size)
                if not in_bytes:
                    break

                self._write_frame_to_output(in_bytes, self.target_fps)

            process.wait()
        except ffmpeg.Error as e:
            raise RuntimeError(f"ffmpeg error while increasing fps: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in _increase_fps: {e}")

    def _calculate_size(self):
        """Computes downscale size for any aspect ratio if more than HD number of pixels"""
        gcd = math.gcd(self.frame_width, self.frame_height)
        aspect_width = self.frame_width // gcd
        aspect_height = self.frame_height // gcd
        
        if self.frame_height < self.frame_width:
            w = self.target_size
            h = ((aspect_height/aspect_width) * w)
        
        elif self.frame_height > self.frame_width:
            h = self.target_size
            w = ((aspect_width/aspect_height) * h)
        
        elif self.frame_height == self.frame_width:
            w = h = self.target_size
        
        size = f"{int(w)}x{int(h)}"
        return size

    def _write_frame_to_output(self, frame_bytes, fps):
        """Writes frames to the output file"""
        try:
            if not hasattr(self, 'out'):
                if (self.frame_height*self.frame_width) > 921600:
                    s = self._calculate_size()
                    
                    self.out = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(self.frame_width, self.frame_height))
                    self.out = ffmpeg.output(self.out, self.output_video_path, pix_fmt='yuv420p', vcodec='libx264', r=fps, s=s)
                    self.out = self.out.overwrite_output().run_async(pipe_stdin=True)
                else:
                    self.out = ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(self.frame_width, self.frame_height))
                    self.out = ffmpeg.output(self.out, self.output_video_path, pix_fmt='yuv420p', vcodec='libx264', r=fps)
                    self.out = self.out.overwrite_output().run_async(pipe_stdin=True)

            self.out.stdin.write(frame_bytes)
                
        except ffmpeg.Error as e:
            raise RuntimeError(f"ffmpeg error while writing frame to output: {e}")
        except Exception as e:
            raise RuntimeError(f"Error in _write_frame_to_output: {e}")

    def close_output(self):
        """Closes the output stream"""
        if hasattr(self, 'out'):
            try:
                self.out.stdin.close()
                self.out.wait()
            except ffmpeg.Error as e:
                raise RuntimeError(f"ffmpeg error while closing output: {e}")
            except Exception as e:
                raise RuntimeError(f"Error in close_output: {e}")

if __name__ == "__main__":
    input_video_path = 'OCR/data/video/webm_test.webm'
    output_video_path = 'OCR/data/video/output_video_fffps.mp4'
    video_loader = VideoNormalizer(input_video_path, 
                                output_video_path, 
                                target_fps=24, 
                                target_size=1280, 
                                fps_lower_bound = 24, 
                                fps_higher_bound = 30)
    video_loader.process_video()
    video_loader.close_output()
