import { Box, Button, IconButton, ToggleButtonGroup } from "@mui/joy";
import { useRef, ChangeEvent } from "react";
import {
  VideoPlayerController,
  useFrameChangeEvent,
} from "./VideoPlayerController";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";
import PauseIcon from "@mui/icons-material/Pause";
import AllInclusiveIcon from '@mui/icons-material/AllInclusive';
import * as styles from "./VideoNavigation.module.scss";

export interface VideoNavigationProps {
  readonly videoPlayerController: VideoPlayerController;
}

export function VideoNavigation(props: VideoNavigationProps) {
  const sliderElementRef = useRef<HTMLInputElement | null>(null);

  const playbackSlowdown = props.videoPlayerController.playbackSlowdown;
  const setPlaybackSlowdown = props.videoPlayerController.setPlaybackSlowdown;
  const isLooping = props.videoPlayerController.isLooping;
  const setIsLooping = props.videoPlayerController.setIsLooping;

  function updateNavigationPosition(frameIndex: number) {
    if (sliderElementRef.current === null) return;

    sliderElementRef.current.value = String(frameIndex);
  }

  useFrameChangeEvent(props.videoPlayerController, (e) =>
    updateNavigationPosition(e.frameIndex),
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
    <Box
      sx={{
        display: "flex",
        flexDirection: "row",
        padding: 1,
        alignItems: "center",
      }}
    >
      <IconButton onClick={handlePlayPauseClick} sx={{ marginRight: 1 }}>
        {props.videoPlayerController.isPlaying ? (
          <PauseIcon />
        ) : (
          <PlayArrowIcon />
        )}
      </IconButton>
      <Box sx={{ flexGrow: 1, display: "flex" }}>
        <input
          className={styles["sliderInput"]}
          ref={sliderElementRef}
          type="range"
          min={0}
          max={props.videoPlayerController.videoFile.frame_count - 1}
          step={1}
          style={{
            flexGrow: 1,
          }}
          onChange={onSliderChange}
        />
      </Box>
      <ToggleButtonGroup
        variant="outlined"
        size="sm"
        sx={{ marginLeft: 2 }}
        value={String(playbackSlowdown)}
        onChange={(event, newValue) => setPlaybackSlowdown(Number(newValue))}
      >
        <Button value="1">1</Button>
        <Button value="2">½</Button>
        <Button value="4">¼</Button>
      </ToggleButtonGroup>
      <IconButton
        size="sm"
        variant="outlined"
        sx={{ marginLeft: 1 }}
        aria-pressed={isLooping ? 'true' : 'false'}
        onClick={() => setIsLooping(!isLooping)}
      >
        <AllInclusiveIcon />
      </IconButton>
    </Box>
  );
}
