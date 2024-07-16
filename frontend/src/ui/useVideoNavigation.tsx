import { Box, Button } from "@mui/joy";
import { useRef, ChangeEvent } from "react";
import { VideoFile } from "../api/model/Video";

export interface VideoNavigationProps {
  readonly videoFile: VideoFile;
  readonly isPlaying: boolean;
  readonly onSeek?: (frameIndex: number, timeSeconds: number) => void;
  readonly onPlay?: () => void;
  readonly onPause?: () => void;
}

export interface VideoNavigationOutput {
  readonly elements: JSX.Element;
  readonly updateNavigationPosition: (frameIndex: number) => void;
}

export function useVideoNavigation(
  props: VideoNavigationProps
): VideoNavigationOutput {
  const sliderElementRef = useRef<HTMLInputElement | null>(null);

  function updateNavigationPosition(frameIndex: number) {
    if (sliderElementRef.current === null) return;
    
    sliderElementRef.current.value = String(frameIndex);
  }

  function onSliderChange(e: ChangeEvent<HTMLInputElement>) {
    const frameIndex = Number(e.target.value);
    const timeSeconds = (
      (frameIndex / props.videoFile.frame_count)
      * props.videoFile.duration_seconds
    );
    if (props.onSeek !== undefined) {
      props.onSeek(frameIndex, timeSeconds)
    }
  }

  function handlePlayPauseClick() {
    if (props.isPlaying) {
      if (props.onPause !== undefined) {
        props.onPause();
      }
    } else {
      if (props.onPlay !== undefined) {
        props.onPlay();
      }
    }
  }
  
  const elements = (
    <Box sx={{ background: "tomato", padding: "24px" }}>
      Video navigation:
      <Button onClick={handlePlayPauseClick}>
        { props.isPlaying ? "Pause" : "Play" }
      </Button>
      <input
        ref={sliderElementRef}
        type="range"
        min={0}
        max={props.videoFile.frame_count}
        step={1}
        style={{ width: "900px" }}
        onChange={onSliderChange}
      ></input>
    </Box>
  );

  return {
    elements,
    updateNavigationPosition,
  }
}