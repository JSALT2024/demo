import { useCallback, useEffect } from "react";
import { VideoPlayerController } from "./VideoPlayerController";

export interface KeyboardShortcutsProps {
  readonly videoPlayerController: VideoPlayerController;
}

export function useKeyboardShortcuts(props: KeyboardShortcutsProps) {
  const controller = props.videoPlayerController;

  const handleKeydown = useCallback(
    (e: KeyboardEvent) => {
      // ignore events targetted at text-input elements
      if (e.target instanceof HTMLInputElement) {
        if (e.type === "text") return;
        if (e.type === "email") return;
        if (e.type === "password") return;
        if (e.type === "date") return;
        // NOTE: add your favourite input type...
      }
      if (e.target instanceof HTMLTextAreaElement) return;

      // spacebar plays/pauses the video
      if (e.key === " ") {
        if (controller.isPlaying) {
          controller.pause();
        } else {
          controller.play();
        }
        e.preventDefault();
      }

      // seek one frame forward
      if (e.key === "ArrowRight") {
        controller.seekToFrame(controller.currentFrameIndexRef.current + 1);
        e.preventDefault();
      }

      // seek one frame backward
      if (e.key === "ArrowLeft") {
        controller.seekToFrame(controller.currentFrameIndexRef.current - 1);
        e.preventDefault();
      }

      // toggle looping
      if (e.key.toUpperCase() === "L") {
        controller.setIsLooping(!controller.isLooping);
        e.preventDefault();
      }

      // set playback speed to 1x
      if (e.key.toUpperCase() === "Q") {
        controller.setPlaybackSlowdown(1);
        e.preventDefault();
      }

      // set playback speed to 1/2x
      if (e.key.toUpperCase() === "W") {
        controller.setPlaybackSlowdown(2);
        e.preventDefault();
      }

      // set playback speed to 1/4x
      if (e.key.toUpperCase() === "E") {
        controller.setPlaybackSlowdown(4);
        e.preventDefault();
      }

      // picture in picture
      if (e.key.toUpperCase() === "P") {
        controller.requestPictureInPicture();
        e.preventDefault();
      }

      // console.log(e.key);
    },
    [controller],
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeydown);
    return () => {
      document.removeEventListener("keydown", handleKeydown);
    };
  }, [controller]);
}
