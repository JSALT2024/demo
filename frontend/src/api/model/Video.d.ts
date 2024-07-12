export interface VideoFile {
  media_type: string;
  duration_seconds: number;
  frame_count: number;
  framerate: number;
  frame_width: number;
  frame_height: number;
  file_size_bytes: number;
}

export interface Video {
  id: string;
  title: string;
  created_at: string;
  uploaded_file: VideoFile;
  normalized_file: VideoFile;
}
