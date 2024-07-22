import * as d3 from "d3";
import { FrameGeometry } from "../../api/model/FrameGeometry";
import { VideoPlayerController } from "./VideoPlayerController";

export interface Rectangle {
  readonly x: number;
  readonly y: number;
  readonly w: number;
  readonly h: number;
}

export function renderLandmarks(
  svg: SVGSVGElement,
  htmlClassName: string,
  color: string,
  videoRectPct: Rectangle,
  videoVpx2PctScale: number,
  landmarksInVpx: number[][] | null,
  radius: number,
) {
  d3.select(svg)
    .selectAll("circle." + htmlClassName)
    .data(landmarksInVpx || [])
    .join("circle")
    .attr("class", htmlClassName)
    .attr("cx", (d) => String(videoRectPct.x + d[0] * videoVpx2PctScale) + "%")
    .attr("cy", (d) => String(videoRectPct.y + d[1] * videoVpx2PctScale) + "%")
    .attr("r", radius)
    .attr("fill", color)
    .attr("opacity", 0.7);
}

export function renderBbox(
  svg: SVGSVGElement,
  htmlClassName: string,
  color: string,
  videoRectPct: Rectangle,
  videoVpx2PctScale: number,
  bboxInVpx: number[] | null,
  thickness: number,
) {
  let rect: Rectangle | null = null;
  if (bboxInVpx !== null) {
    rect = {
      x: bboxInVpx[0],
      y: bboxInVpx[1],
      w: bboxInVpx[2] - bboxInVpx[0],
      h: bboxInVpx[3] - bboxInVpx[1],
    };
  }

  d3.select(svg)
    .selectAll("rect." + htmlClassName)
    .data(rect === null ? [] : [rect])
    .join("rect")
    .attr("class", htmlClassName)
    .attr("x", (d) => String(videoRectPct.x + d.x * videoVpx2PctScale) + "%")
    .attr("y", (d) => String(videoRectPct.y + d.y * videoVpx2PctScale) + "%")
    .attr("width", (d) => String(d.w * videoVpx2PctScale) + "%")
    .attr("height", (d) => String(d.h * videoVpx2PctScale) + "%")
    .attr("stroke", color)
    .attr("stroke-width", String(thickness))
    .attr("fill", "transparent")
    .attr("opacity", 0.7);
}

export function renderPreviewOverlay(
  overlaySvg: SVGSVGElement,
  frameGeometry: FrameGeometry,
  videoRectPct: Rectangle,
  videoVpx2PctScale: number,
  controller: VideoPlayerController,
) {
  // overlay the pose
  renderLandmarks(
    overlaySvg,
    "pose",
    "lime",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayPose ? frameGeometry.pose_landmarks : null,
    3,
  );
  renderBbox(
    overlaySvg,
    "pose",
    "lime",
    videoRectPct,
    videoVpx2PctScale,
    frameGeometry.sign_space, // NOTE sign space is always visible
    2,
  );

  // overlay the face
  renderLandmarks(
    overlaySvg,
    "face",
    "tomato",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayFace ? frameGeometry.face_landmarks : null,
    1,
  );
  renderBbox(
    overlaySvg,
    "face",
    "tomato",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayFace ? frameGeometry.face_bbox : null,
    1,
  );

  // overlay the left hand
  renderLandmarks(
    overlaySvg,
    "left-hand",
    "cyan",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayLeftHand ? frameGeometry.left_hand_landmarks : null,
    2,
  );
  renderBbox(
    overlaySvg,
    "left-hand",
    "cyan",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayLeftHand ? frameGeometry.left_hand_bbox : null,
    1,
  );

  // overlay the right hand
  renderLandmarks(
    overlaySvg,
    "right-hand",
    "yellow",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayRightHand ? frameGeometry.right_hand_landmarks : null,
    2,
  );
  renderBbox(
    overlaySvg,
    "right-hand",
    "yellow",
    videoRectPct,
    videoVpx2PctScale,
    controller.overlayRightHand ? frameGeometry.right_hand_bbox : null,
    1,
  );
}
