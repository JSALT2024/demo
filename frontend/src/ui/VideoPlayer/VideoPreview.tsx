import { Box } from "@mui/joy";
import { VideoPlayerController, useFrameChangeEvent } from "./VideoPlayerController";
import { FixedAspectBox } from "./FixedAspectBox";
import { CSSProperties, useRef } from "react";
import { FrameGeometry, buildMissingFrameGeometry } from "../../api/model/FrameGeometry";
import * as d3 from "d3";
import { SxProps } from "@mui/joy/styles/types";

export interface VideoPreviewProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly videoBlobUrl: string;
  readonly frameGeometries: FrameGeometry[];
  readonly sx?: SxProps;
}

function sigmoid(z) {
  return 1 / (1 + Math.exp(-z));
}

function lerp(t, a, b) {
  return a + t * (b - a);
}

export function VideoPreview(props: VideoPreviewProps) {
  const signingSpaceSvgRectRef = useRef<SVGRectElement | null>(null);
  const bodyPoseSvgRef = useRef<SVGSVGElement | null>(null);

  // how much smaller is the signing space compared to the preview square
  const zoomScaling = 0.8;

  function onFrameChange(frameIndex: number) {
    // TODO: DEBUG: scale when rendering
    // const zoomScaling = (
    //   1 - (frameIndex / props.videoPlayerController.videoFile.frame_count)
    // );

    // fetch data for the frame
    const frameGeometry: FrameGeometry = (
      props.frameGeometries[frameIndex] || buildMissingFrameGeometry(
        props.videoPlayerController.videoFile
      )
    );
    
    // signing space in video-pixel coordinates
    const signingSpaceVpx = {
      x: frameGeometry.sign_space[0],
      y: frameGeometry.sign_space[1],
      w: frameGeometry.sign_space[2] - frameGeometry.sign_space[0],
      h: frameGeometry.sign_space[3] - frameGeometry.sign_space[1],
    };

    // frame size in video-pixel coordinates
    const frameSizeVpx = {
      w: props.videoPlayerController.videoFile.frame_width,
      h: props.videoPlayerController.videoFile.frame_height,
    };

    // signing space box coordinates in the preview percentage coordinates
    const signingSpacePct = {
      x: 50 - 50 * zoomScaling,
      y: 50 - 50 * zoomScaling,
      w: zoomScaling * 100,
      h: zoomScaling * 100,
    };

    // converts vpx length units to pct length units
    const videoVpx2PctScale = signingSpacePct.w / signingSpaceVpx.w;

    // position the video element inside the preview percentage coordinates
    const videoRectPct = {
      x: signingSpacePct.x + (-signingSpaceVpx.x * videoVpx2PctScale),
      y: signingSpacePct.y + (-signingSpaceVpx.y * videoVpx2PctScale),
      w: frameSizeVpx.w * videoVpx2PctScale,
      h: frameSizeVpx.h * videoVpx2PctScale,
    };

    // position the video element
    if (props.videoPlayerController.videoElementRef.current !== null) {
      const e = props.videoPlayerController.videoElementRef.current;
      e.style.left = String(videoRectPct.x) + "%";
      e.style.top = String(videoRectPct.y) + "%";
      e.style.width = String(videoRectPct.w) + "%";
      e.style.height = String(videoRectPct.h) + "%";
    }

    // position the signing space rectangle
    if (signingSpaceSvgRectRef.current !== null) {
      const e = signingSpaceSvgRectRef.current;
      e.setAttribute("x", String(signingSpacePct.x) + "%");
      e.setAttribute("y", String(signingSpacePct.y) + "%");
      e.setAttribute("width", String(signingSpacePct.w) + "%");
      e.setAttribute("height", String(signingSpacePct.h) + "%");
    }

    // display the body pose
    if (bodyPoseSvgRef.current !== null) {
      const e = bodyPoseSvgRef.current;
      d3.select(e)
        .selectAll("circle")
        .data(frameGeometry.pose_landmarks || [])
        .join("circle")
        .attr("cx", d => String(videoRectPct.x + d[0] * videoVpx2PctScale) + "%")
        .attr("cy", d => String(videoRectPct.y + d[1] * videoVpx2PctScale) + "%")
        // .attr("r", d => lerp((-d[2] / signingSpaceVpx.w) * 100 + 0.1, 2, 50))
        .attr("r", 5)
        .attr("opacity", d => sigmoid(d[3]))
        .attr("fill", "lime");
    }
  }

  useFrameChangeEvent(
    props.videoPlayerController,
    e => onFrameChange(e.frameIndex)
  );

  const FILL_STYLE: CSSProperties = {
    position: "absolute",
    top: "0%",
    left: "0%",
    width: "100%",
    height: "100%",
  };

  return (
    <FixedAspectBox
      aspectRatio={1 / 1}
      sx={{ ...props.sx, background: "black" }}
    >
      {/* Video element */}
      <video
        ref={props.videoPlayerController.videoElementRef}
        style={FILL_STYLE}
        src={props.videoBlobUrl}
        muted={true}
        controls={false}
        onCanPlay={props.videoPlayerController.video_onCanPlay}
        onSeeked={props.videoPlayerController.video_onSeeked}
        onPlay={props.videoPlayerController.video_onPlay}
        onPause={props.videoPlayerController.video_onPause}
      ></video>

      {/* signing space overlay */}
      <svg style={FILL_STYLE}>
        <rect
          ref={signingSpaceSvgRectRef}
          stroke="lime"
          strokeWidth="2"
          fill="transparent"
        />
      </svg>

      {/* body pose overlay */}
      <svg style={FILL_STYLE} ref={bodyPoseSvgRef}>
        <circle
          cx="50%"
          cy="50%"
          r="2"
          fill="lime"
        />
      </svg>
    </FixedAspectBox>
  )
}
