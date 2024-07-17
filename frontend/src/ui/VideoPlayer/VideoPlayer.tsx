import { Box } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../../api/model/Video";
import { VideoNavigation } from "./VideoNavigation";
import { useFrameChangeEvent, useVideoPlayerController } from "./VideoPlayerController";
import * as d3 from "d3";
import { VideoPreview } from "./VideoPreview";
import { FrameGeometry } from "../../api/model/FrameGeometry";

export interface VideoPlayerProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
  readonly frameGeometries: FrameGeometry[];
}

export function VideoPlayer(props: VideoPlayerProps) {
  const videoPlayerController = useVideoPlayerController({
    videoFile: props.videoFile,
  });

  const debugElementRef = useRef<HTMLPreElement | null>(null);

  function onFrameChange(frameIndex: number) {
    if (debugElementRef.current === null) return;
    debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);
  }

  useFrameChangeEvent(
    videoPlayerController,
    e => onFrameChange(e.frameIndex)
  );
  
  return (
    <Box>
      <VideoPreview
        videoBlobUrl={props.videoBlobUrl}
        videoPlayerController={videoPlayerController}
        frameGeometries={props.frameGeometries}
      />

      <pre ref={debugElementRef}></pre>

      <VideoNavigation videoPlayerController={videoPlayerController} />
    </Box>
  );
}
