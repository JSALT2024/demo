import { Box } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../api/model/Video";
import { useVideoFrameTracking } from "./useVideoFrameTracking";
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

  function onFrameChange(frameIndex: number) {
    if (debugElementRef.current === null) return;
    debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);

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
        width={512}
        controls
        onCanPlay={frameTracking.onCanPlay}
        onSeeked={frameTracking.onSeeked}
      ></video>

      <svg ref={svgElementRef} width={512} height={512}>
        <circle r={10} fill="tomato" />
      </svg>

      <pre ref={debugElementRef}></pre>
    </Box>
  );
}
