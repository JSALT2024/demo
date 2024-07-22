import {
  VideoPlayerController,
  useFrameChangeEvent,
} from "./VideoPlayerController";
import { FixedAspectBox } from "./FixedAspectBox";
import { CSSProperties, useRef } from "react";
import {
  FrameGeometry,
  buildMissingFrameGeometry,
} from "../../api/model/FrameGeometry";
import { SxProps } from "@mui/joy/styles/types";
import { useApplyVideoBlob } from "./useApplyVideoBlob";
import { renderPreviewOverlay } from "./renderPreviewOverlay";

export interface VideoPreviewProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly videoBlob: Blob | null;
  readonly frameGeometries: FrameGeometry[] | null;
  readonly sx?: SxProps;
}

export function VideoPreview(props: VideoPreviewProps) {
  const overlaySvgRef = useRef<SVGSVGElement | null>(null);

  // how much smaller is the signing space compared to the preview square
  const zoomScaling = 0.9;

  function onFrameChange(frameIndex: number) {
    // fetch data for the frame
    const frameGeometry: FrameGeometry =
      props.frameGeometries?.[frameIndex] ||
      buildMissingFrameGeometry(props.videoPlayerController.videoFile);

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
      x: signingSpacePct.x + -signingSpaceVpx.x * videoVpx2PctScale,
      y: signingSpacePct.y + -signingSpaceVpx.y * videoVpx2PctScale,
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

    // render the overlay
    if (overlaySvgRef.current !== null) {
      renderPreviewOverlay(
        overlaySvgRef.current,
        frameGeometry,
        videoRectPct,
        videoVpx2PctScale,
        props.videoPlayerController,
      );
    }
  }

  useFrameChangeEvent(
    props.videoPlayerController,
    (e) => onFrameChange(e.frameIndex),
    [props.frameGeometries, props.videoPlayerController],
  );

  // set the video blob to the video element
  useApplyVideoBlob({
    videoBlob: props.videoBlob,
    videoPlayerController: props.videoPlayerController,
  });

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
        muted={true}
        controls={false}
        onCanPlay={props.videoPlayerController.video_onCanPlay}
        onSeeked={props.videoPlayerController.video_onSeeked}
        onPlay={props.videoPlayerController.video_onPlay}
        onPause={props.videoPlayerController.video_onPause}
      ></video>

      {/* video preview overlay */}
      <svg style={FILL_STYLE} ref={overlaySvgRef}></svg>
    </FixedAspectBox>
  );
}
