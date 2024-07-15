import { Box } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../api/model/Video";
import { useVideoFrameTracking } from "./useVideoFrameTracking";

export interface VideoRendererProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
}

export function VideoRenderer(props: VideoRendererProps) {
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const debugElementRef = useRef<HTMLPreElement | null>(null);

  function onFrameChange(frameIndex: number) {
    if (debugElementRef.current === null) return;
    debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);
  }

  const frameTracking = useVideoFrameTracking({
    videoElementRef,
    framerate: props.videoFile.framerate,
    onFrameChange,
  });

  return (
    <Box>
      <video
        ref={videoElementRef}
        src={props.videoBlobUrl}
        muted
        width={512}
        controls
        onCanPlay={frameTracking.onCanPlay}
        onSeeked={frameTracking.onSeeked}
      ></video>

      <pre ref={debugElementRef}></pre>
    </Box>
  );
}
