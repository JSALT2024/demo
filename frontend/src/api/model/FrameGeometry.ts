import { VideoFile } from "./Video";

export interface FrameGeometry {
  readonly pose_landmarks: number[][] | null;
  readonly sign_space: number[];
}

export function buildMissingFrameGeometry(videoFile: VideoFile): FrameGeometry {
  const sign_space_size = Math.min(
    videoFile.frame_width,
    videoFile.frame_height
  );

  return {
    pose_landmarks: [],
    sign_space: [0, 0, sign_space_size, sign_space_size],
  }
}
