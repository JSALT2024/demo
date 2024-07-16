import { Box, Button } from "@mui/joy";
import { useRef, ChangeEvent } from "react";
import { VideoPlayerController, useFrameChangeEvent } from "./VideoPlayerController";

export interface VideoNavigationProps {
  readonly videoPlayerController: VideoPlayerController;
}

export function VideoNavigation(props: VideoNavigationProps) {
  const sliderElementRef = useRef<HTMLInputElement | null>(null);

  function updateNavigationPosition(frameIndex: number) {
    if (sliderElementRef.current === null) return;
    
    sliderElementRef.current.value = String(frameIndex);
  }

  useFrameChangeEvent(
    props.videoPlayerController,
    e => updateNavigationPosition(e.frameIndex)
  );

  function onSliderChange(e: ChangeEvent<HTMLInputElement>) {
    const frameIndex = Number(e.target.value);
    props.videoPlayerController.seekToFrame(frameIndex);
  }

  function handlePlayPauseClick() {
    if (props.videoPlayerController.isPlaying) {
      props.videoPlayerController.pause();
    } else {
      props.videoPlayerController.play();
    }
  }
  
  return (
    <Box sx={{ background: "tomato", padding: "24px" }}>
      Video navigation:
      <Button onClick={handlePlayPauseClick}>
        { props.videoPlayerController.isPlaying ? "Pause" : "Play" }
      </Button>
      <input
        ref={sliderElementRef}
        type="range"
        min={0}
        max={props.videoPlayerController.videoFile.frame_count}
        step={1}
        style={{ width: "900px" }}
        onChange={onSliderChange}
      ></input>
    </Box>
  );
}