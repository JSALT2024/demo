import { MutableRefObject, useRef, useEffect, useCallback, ReactEventHandler } from "react";

function getPaintCount(video: HTMLVideoElement): number | undefined {
  return (
    (video as any).mozPaintedFrames
    || (video as any).webkitDecodedFrameCount
    || undefined
  );
}

export interface VideoFrameTrackingProps {
  readonly videoElementRef: MutableRefObject<HTMLVideoElement | null>;
  readonly framerate: number;

  /**
   * Called whenever the current frame number changes,
   * plus called during the initial load
   */
  readonly onFrameChange: (frameIndex: number) => void;
}

export interface VideoFrameTrackingOutput {
  // bind these to the video element events
  readonly onCanPlay: ReactEventHandler<HTMLVideoElement>;
  readonly onSeeked: ReactEventHandler<HTMLVideoElement>;
}

/**
 * Provides the logic for tracking the current frame of an HTML video element.
 * Based on: https://github.com/Daiz/frame-accurate-ish
 */
export function useVideoFrameTracking(
  props: VideoFrameTrackingProps
): VideoFrameTrackingOutput {
  const dependencies = [props.framerate];

  // constants about the video
  const FPS = props.framerate;
  const FRAME = 1 / FPS;
  const FRAME_WINDOW_LOWER = FRAME * 0.95;
  const FRAME_WINDOW_UPPER = FRAME * 0.25;
  
  // state of the tracker
  const driftRef = useRef<number | null>(null);
  const currentFrameRef = useRef<number>(0);
  const nextFrameRef = useRef<number>(1);
  const nextFrameTimeRef = useRef<number>(1 * FRAME);
  const lastPaintCountRef = useRef<number>(0);

  // event firing
  const lastFrameReportedRef = useRef<number>(0);

  // tracks the animation frame request so that it can be cancelled
  const requestNumberRef = useRef<number | null>(null);

  const onCanPlay = useCallback(() => {
    if (props.videoElementRef.current === null) return;

    if (driftRef.current == null) {
      driftRef.current = props.videoElementRef.current.currentTime;
    }
  }, [...dependencies]);

  const onSeeked = useCallback(() => {
    if (props.videoElementRef.current === null) return;
    const videoElement = props.videoElementRef.current;

    // code taken from Daiz
    const time = videoElement.currentTime - (driftRef.current || 0);
    const frame = Math.floor(time / FRAME);
    currentFrameRef.current = frame;
    nextFrameRef.current = frame + 1;
    nextFrameTimeRef.current = nextFrameRef.current * FRAME;
    const paintCount = getPaintCount(videoElement);
    if (paintCount !== undefined) {
      lastPaintCountRef.current = paintCount;
    }
  }, [...dependencies]);

  // called for each animation frame
  const loop = useCallback(() => {
    if (props.videoElementRef.current === null) return;
    const videoElement = props.videoElementRef.current;

    // code taken from Daiz
    const time = videoElement.currentTime - (driftRef.current || 0);
    const frame = Math.round(time / FRAME);
    const paintCount = getPaintCount(videoElement);
    if (paintCount !== undefined) {
      const currentPaintCount = paintCount;
      const diffPaintCount = currentPaintCount - lastPaintCountRef.current;
      const check = (
        time >= nextFrameTimeRef.current - FRAME_WINDOW_LOWER
        && time <= nextFrameTimeRef.current + FRAME_WINDOW_UPPER
      );
      if (check && diffPaintCount > 0) {
        currentFrameRef.current = nextFrameRef.current++;
        nextFrameTimeRef.current = nextFrameRef.current * FRAME;
      } else if (
        time >= nextFrameTimeRef.current
        && currentFrameRef.current < nextFrameRef.current
      ) {
        currentFrameRef.current = frame;
        nextFrameRef.current = currentFrameRef.current + 1;
        nextFrameTimeRef.current = nextFrameRef.current * FRAME;
      }
      lastPaintCountRef.current = currentPaintCount;
    } else {
      currentFrameRef.current = frame;
    }

    // fire the change event
    if (lastFrameReportedRef.current !== currentFrameRef.current) {
      props.onFrameChange(currentFrameRef.current);
      lastFrameReportedRef.current = currentFrameRef.current;
    }

    // keep the animation running
    requestNumberRef.current = requestAnimationFrame(loop);
  }, [...dependencies]);

  // handles registration and freeing of the animation frame callback
  useEffect(() => {
    // fire the initial event
    props.onFrameChange(currentFrameRef.current);
    lastFrameReportedRef.current = currentFrameRef.current;

    // start the loop
    requestNumberRef.current = requestAnimationFrame(loop);

    // stop the loop
    return () => {
      if (requestNumberRef.current !== null) {
        cancelAnimationFrame(requestNumberRef.current);
      }
    };
  }, [...dependencies]);
  
  return {
    onCanPlay,
    onSeeked,
  };
}