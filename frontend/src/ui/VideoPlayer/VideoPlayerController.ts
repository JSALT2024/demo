import {
  MutableRefObject,
  useEffect,
  useMemo,
  useRef,
  useState,
  SyntheticEvent,
  SetStateAction,
  Dispatch,
} from "react";
import { VideoFile } from "../../api/model/Video";
import { useVideoFrameTracking } from "./useVideoFrameTracking";

export interface FrameChangeEvent {
  readonly frameIndex: number;
}

export type FrameChangeEventHandler = (event: FrameChangeEvent) => void;

export interface VideoPlayerControllerProps {
  readonly videoFile: VideoFile;
}

/**
 * Provides vanilla-js access to the video player, bypassing react so that
 * we get maximal performance and avoid lagging for frame-based changes.
 *
 * It pretends to be a react state value so you can pass it around as such.
 */
export interface VideoPlayerController {
  readonly videoElementRef: MutableRefObject<HTMLVideoElement | null>;
  readonly isPlaying: boolean;
  readonly videoFile: VideoFile;
  readonly currentFrameIndexRef: MutableRefObject<number>;

  readonly overlayPose: boolean;
  readonly overlayFace: boolean;
  readonly overlayLeftHand: boolean;
  readonly overlayRightHand: boolean;
  readonly setOverlayPose: Dispatch<SetStateAction<boolean>>;
  readonly setOverlayFace: Dispatch<SetStateAction<boolean>>;
  readonly setOverlayLeftHand: Dispatch<SetStateAction<boolean>>;
  readonly setOverlayRightHand: Dispatch<SetStateAction<boolean>>;

  readonly _frameChangeEventHandlersRef: any;

  readonly seekToFrame: (frameIndex: number) => void;
  readonly play: () => void;
  readonly pause: () => void;

  readonly addFrameChangeEventListener: (
    handler: FrameChangeEventHandler,
  ) => void;
  readonly removeFrameChangeEventListener: (
    handler: FrameChangeEventHandler,
  ) => void;

  readonly video_onCanPlay: (e: SyntheticEvent<HTMLVideoElement>) => void;
  readonly video_onSeeked: (e: SyntheticEvent<HTMLVideoElement>) => void;
  readonly video_onPlay: (e: SyntheticEvent<HTMLVideoElement>) => void;
  readonly video_onPause: (e: SyntheticEvent<HTMLVideoElement>) => void;
}

/**
 * Creates a video player controller and returns it for use
 */
export function useVideoPlayerController(
  props: VideoPlayerControllerProps,
): VideoPlayerController {
  // state of the controller
  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const frameChangeEventHandlersRef = useRef<FrameChangeEventHandler[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const currentFrameIndexRef = useRef<number>(0);

  const [overlayPose, setOverlayPose] = useState<boolean>(true);
  const [overlayFace, setOverlayFace] = useState<boolean>(true);
  const [overlayLeftHand, setOverlayLeftHand] = useState<boolean>(true);
  const [overlayRightHand, setOverlayRightHand] = useState<boolean>(true);

  function onFrameChange(frameIndex: number) {
    // clamp the frame index to the video frames (because it sometimes runs)
    // one frame after the end of the video due to the +-1 acuracy of tracking
    if (frameIndex >= props.videoFile.frame_count) {
      frameIndex = props.videoFile.frame_count - 1;
    }
    if (frameIndex < 0) {
      frameIndex = 0;
    }

    // remember the current frame index
    currentFrameIndexRef.current = frameIndex;

    // dispatch the frame change event
    const event: FrameChangeEvent = { frameIndex };
    for (const handler of frameChangeEventHandlersRef.current) {
      handler(event);
    }
  }

  // video frame-tracking logic
  const frameTracking = useVideoFrameTracking({
    videoElementRef,
    framerate: props.videoFile.framerate,
    onFrameChange,
  });

  // returned value refreshes when these values change
  // (change in these will trigger React re-render, to watch others you need
  // to subscribe to the corresponding vanilla-js events)
  const memoDependencies = [
    isPlaying,
    props.videoFile,
    overlayPose,
    overlayFace,
    overlayLeftHand,
    overlayRightHand,
  ];

  // returns the object that users use to access the controller
  return useMemo<VideoPlayerController>(
    () => ({
      // readable state
      videoElementRef,
      isPlaying,
      videoFile: props.videoFile,
      currentFrameIndexRef,

      overlayPose,
      overlayFace,
      overlayLeftHand,
      overlayRightHand,
      setOverlayPose,
      setOverlayFace,
      setOverlayLeftHand,
      setOverlayRightHand,

      // private readable state
      _frameChangeEventHandlersRef: frameChangeEventHandlersRef,

      // video player manipulation methods
      seekToFrame(frameIndex: number) {
        if (videoElementRef.current === null) return;
        const timeSeconds =
          (frameIndex / props.videoFile.frame_count) *
          props.videoFile.duration_seconds;
        videoElementRef.current.currentTime = timeSeconds;

        // emulate the event, because the frameTracking code was not really
        // designed for seeking and it might not fire properly
        onFrameChange(frameIndex);
      },
      play() {
        if (videoElementRef.current === null) return;
        videoElementRef.current.play();
        setIsPlaying(true);
      },
      pause() {
        if (videoElementRef.current === null) return;
        videoElementRef.current.pause();
        setIsPlaying(false);
      },

      // frame change event handling
      addFrameChangeEventListener(handler: FrameChangeEventHandler) {
        frameChangeEventHandlersRef.current.push(handler);
        handler({ frameIndex: currentFrameIndexRef.current });
      },
      removeFrameChangeEventListener(handler: FrameChangeEventHandler) {
        const index = frameChangeEventHandlersRef.current.indexOf(handler);
        if (index > -1) {
          frameChangeEventHandlersRef.current.splice(index, 1);
        }
      },

      // video event handlers
      video_onCanPlay(e: SyntheticEvent<HTMLVideoElement>) {
        frameTracking.onCanPlay(e);
      },
      video_onSeeked(e: SyntheticEvent<HTMLVideoElement>) {
        frameTracking.onSeeked(e);
      },
      video_onPlay(e: SyntheticEvent<HTMLVideoElement>) {
        setIsPlaying(true);
      },
      video_onPause(e: SyntheticEvent<HTMLVideoElement>) {
        setIsPlaying(false);
      },
    }),
    memoDependencies,
  );
}

/**
 * Subscribes a frame change event listener for the lifetime of the caller.
 * Provide a list of dependencies to specify when to re-bind the handler
 * function. This should be the list of props the handler function
 * relies on (because the handler function has them attached in its closure
 * otherwise and that needs to be broken)
 */
export function useFrameChangeEvent(
  controller: VideoPlayerController,
  handler: FrameChangeEventHandler,
  dependencies?: any[],
) {
  // analogous to window.onscroll event binding usually done in react
  // (cached based on the "event hub" object identity)
  useEffect(() => {
    controller.addFrameChangeEventListener(handler);
    return () => controller.removeFrameChangeEventListener(handler);
  }, [controller._frameChangeEventHandlersRef, ...(dependencies || [])]);
}
