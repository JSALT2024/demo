import { VideoFile } from "./Video";

export interface FrameGeometry {
  readonly pose_landmarks: number[][] | null;
  readonly right_hand_landmarks: number[][] | null;
  readonly left_hand_landmarks: number[][] | null;
  readonly face_landmarks: number[][] | null;

  readonly sign_space: number[];

  readonly right_hand_bbox: number[] | null;
  readonly left_hand_bbox: number[] | null;
  readonly face_bbox: number[] | null;
}

export function buildMissingFrameGeometry(videoFile: VideoFile): FrameGeometry {
  const sign_space_size = Math.min(
    videoFile.frame_width,
    videoFile.frame_height
  );

  return {
    pose_landmarks: null,
    right_hand_landmarks: null,
    left_hand_landmarks: null,
    face_landmarks: null,

    sign_space: [0, 0, sign_space_size, sign_space_size],

    right_hand_bbox: null,
    left_hand_bbox: null,
    face_bbox: null,
  }
}
