import { VideoPlayerController } from "./VideoPlayerController";

export interface VideoPreviewProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly videoBlobUrl: string;
}

export function VideoPreview(props: VideoPreviewProps) {
  return (
    <video
      ref={props.videoPlayerController.videoElementRef}
      src={props.videoBlobUrl}
      muted
      width={512*0.6}
      controls
      onCanPlay={props.videoPlayerController.video_onCanPlay}
      onSeeked={props.videoPlayerController.video_onSeeked}
      onPlay={props.videoPlayerController.video_onPlay}
      onPause={props.videoPlayerController.video_onPause}
    ></video>
  )
}
