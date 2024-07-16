import { Box } from "@mui/joy";
import { useRef, useState } from "react";
import { VideoFile } from "../api/model/Video";
import { useVideoFrameTracking } from "./useVideoFrameTracking";
import { useVideoNavigation } from "./useVideoNavigation";
import * as d3 from "d3";

export interface VideoRendererProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
}

export function VideoRenderer(props: VideoRendererProps) {
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const debugElementRef = useRef<HTMLPreElement | null>(null);
  const svgElementRef = useRef<SVGSVGElement | null>(null);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const videoNavigation = useVideoNavigation({
    videoFile: props.videoFile,
    isPlaying,
    onSeek(frameIndex, timeSeconds) {
      if (videoElementRef.current === null) return;
      videoElementRef.current.currentTime = timeSeconds;
    },
    onPlay() {
      if (videoElementRef.current === null) return;
      videoElementRef.current.play();
    },
    onPause() {
      if (videoElementRef.current === null) return;
      videoElementRef.current.pause();
    },
  });

  function onFrameChange(frameIndex: number) {
    if (debugElementRef.current === null) return;
    debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);
    
    // update video navigation
    videoNavigation.updateNavigationPosition(frameIndex);

    // update overlay
    const svg = svgElementRef.current;
    d3.select(svg)
      .select("circle")
      .attr("cx", frameIndex)
      .attr("cy", frameIndex)
      .attr("r", 10)
      .style("fill", "tomato");
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
        width={512*0.6}
        controls
        onCanPlay={frameTracking.onCanPlay}
        onSeeked={frameTracking.onSeeked}
        onPlay={() => void setIsPlaying(true)}
        onPause={() => void setIsPlaying(false)}
      ></video>

      <svg ref={svgElementRef} width={512} height={512}>
        <circle r={10} fill="tomato" />
      </svg>

      <pre ref={debugElementRef}></pre>

      { videoNavigation.elements }
    </Box>
  );
}
