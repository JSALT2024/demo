import { Box } from "@mui/joy";
import { VideoPlayerController, useFrameChangeEvent } from "./VideoPlayerController";
import { FixedAspectBox } from "./FixedAspectBox";
import { CSSProperties, useRef } from "react";

export interface VideoPreviewProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly videoBlobUrl: string;
}

export function VideoPreview(props: VideoPreviewProps) {
  
  const signingSpaceSvgRectRef = useRef<SVGRectElement | null>(null);

  // how much smaller is the signing space compared to the preview square
  const zoomScaling = 0.8;

  function onFrameChange(frameIndex: number) {
    // TODO: DEBUG: scale when rendering
    // const zoomScaling = (
    //   1 - (frameIndex / props.videoPlayerController.videoFile.frame_count)
    // );

    // TODO: fetch data for the frame
    
    // signing space in video-pixel coordinates
    const signingSpaceVpx = {
      x: -360,
      y: -50,
      w: 1080 - (-360),
      h: 1390 - (-50),
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
    <Box>
      <FixedAspectBox
        aspectRatio={1 / 1}
        sx={{ width: "400px", border: "1px solid black", background: "black" }}
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

        {/* SVG overlay */}
        <svg style={FILL_STYLE}>
          <rect
            ref={signingSpaceSvgRectRef}
            stroke="lime"
            strokeWidth="2"
            fill="transparent"
          />
        </svg>
      </FixedAspectBox>
    </Box>
  )
}
