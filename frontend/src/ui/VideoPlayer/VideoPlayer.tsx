import { Box } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../../api/model/Video";
import { VideoNavigation } from "./VideoNavigation";
import { useFrameChangeEvent, useVideoPlayerController } from "./VideoPlayerController";
import * as d3 from "d3";
import { VideoPreview } from "./VideoPreview";

export interface VideoPlayerProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
}

export function VideoPlayer(props: VideoPlayerProps) {
  const videoPlayerController = useVideoPlayerController({
    videoFile: props.videoFile,
  });

  const debugElementRef = useRef<HTMLPreElement | null>(null);
  const svgElementRef = useRef<SVGSVGElement | null>(null);

  function onFrameChange(frameIndex: number) {
    if (debugElementRef.current === null) return;
    debugElementRef.current.innerHTML = "Frame: " + String(frameIndex);

    // update overlay
    const svg = svgElementRef.current;
    d3.select(svg)
      .select("circle")
      .attr("cx", frameIndex)
      .attr("cy", frameIndex)
      .attr("r", 10)
      .style("fill", "tomato");
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
      />

      <svg ref={svgElementRef} width={512} height={512}>
        <circle r={10} fill="tomato" />
      </svg>

      <pre ref={debugElementRef}></pre>

      <VideoNavigation videoPlayerController={videoPlayerController} />
    </Box>
  );
}
