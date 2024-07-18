import { Box } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../../api/model/Video";
import { VideoNavigation } from "./VideoNavigation";
import { useFrameChangeEvent, useVideoPlayerController } from "./VideoPlayerController";
import { VideoPreview } from "./VideoPreview";
import { FrameGeometry } from "../../api/model/FrameGeometry";
import { VideoCrops } from "../../api/model/VideoCrops";

export interface VideoPlayerProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
  readonly frameGeometries: FrameGeometry[];
  readonly videoCrops: VideoCrops;
}

export function VideoPlayer(props: VideoPlayerProps) {
  const videoPlayerController = useVideoPlayerController({
    videoFile: props.videoFile,
  });

  const debugElementRef = useRef<HTMLPreElement | null>(null);
  const cropPreviewRef = useRef<HTMLImageElement | null>(null);

  function onFrameChange(frameIndex: number) {
    // update the frame number
    if (debugElementRef.current !== null) {
      debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);
    }

    // update the crop preview
    if (cropPreviewRef.current !== null && props.videoCrops.face[frameIndex]) {
      const e = cropPreviewRef.current;
      const newCropUrl = URL.createObjectURL(props.videoCrops.face[frameIndex]);
      const oldCropUrl = e.src;
      e.src = newCropUrl;
      URL.revokeObjectURL(oldCropUrl);
    }
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

      <img ref={cropPreviewRef} />

      <pre ref={debugElementRef}></pre>

      <VideoNavigation videoPlayerController={videoPlayerController} />
    </Box>
  );
}
