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
import { ClipsCollection } from "../../api/model/ClipsCollection";

export interface VideoNavigationProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly clipsCollection: ClipsCollection | null;
}

export function VideoNavigation(props: VideoNavigationProps) {
  const sliderElementRef = useRef<HTMLInputElement | null>(null);
  const progessElementRef = useRef<HTMLElement | null>(null);

  const playbackSlowdown = props.videoPlayerController.playbackSlowdown;
  const setPlaybackSlowdown = props.videoPlayerController.setPlaybackSlowdown;
  const isLooping = props.videoPlayerController.isLooping;
  const setIsLooping = props.videoPlayerController.setIsLooping;

  function frameToCssPercentage(frame: number): string {
    return String(
      frame / props.videoPlayerController.videoFile.frame_count * 100
    ) + "%";
  }

  function updateNavigationPosition(frameIndex: number) {
    if (sliderElementRef.current === null) return;
    if (progessElementRef.current === null) return;

    sliderElementRef.current.value = String(frameIndex);
    progessElementRef.current.style.width = frameToCssPercentage(frameIndex);
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
      {/* Play/Pause button */}
      <IconButton onClick={handlePlayPauseClick} sx={{ marginRight: 1 }}>
        {props.videoPlayerController.isPlaying ? (
          <PauseIcon />
        ) : (
          <PlayArrowIcon />
        )}
      </IconButton>

      {/* Time navigation slider */}
      <Box sx={{ flexGrow: 1, display: "flex", position: "relative" }}>
        {/* Clip boundaries */}
        {props.clipsCollection && (
          <svg
            style={{
              position: "absolute",
              top: "50%",
              height: "18px",
              left: 0,
              width: "100%",
              pointerEvents: "none",
              transform: "translateY(-50%)",
            }}
          >
            {props.clipsCollection.clips.slice(1).map(clip => (
              <line
                key={clip.clip_index}
                x1={frameToCssPercentage(clip.start_frame)}
                x2={frameToCssPercentage(clip.start_frame)}
                y1="0%"
                y2="100%"
                strokeWidth="2px"
                stroke="var(--joy-palette-neutral-300)"
              />
            ))}
          </svg>
        )}

        {/* HTML slider element */}
        <input
          className={styles["sliderInput"]}
          ref={sliderElementRef}
          type="range"
          min={0}
          max={props.videoPlayerController.videoFile.frame_count - 1}
          step={1}
          style={{
            flexGrow: 1,
            position: "relative",
          }}
          onChange={onSliderChange}
        />

        {/* Progress filling color */}
        <Box
          ref={progessElementRef}
          sx={{
            position: "absolute",
            top: 0,
            bottom: 0,
            left: 0,
            width: "50%",
            background: "var(--joy-palette-primary-500)",
            pointerEvents: "none",
          }}
        ></Box>
      </Box>

      {/* Playback slowdown toggle buttons */}
      <ToggleButtonGroup
        variant="outlined"
        size="sm"
        sx={{ marginLeft: 2 }}
        value={String(playbackSlowdown)}
        onChange={(_, newValue) => setPlaybackSlowdown(Number(newValue))}
      >
        <Button value="1">1</Button>
        <Button value="2">½</Button>
        <Button value="4">¼</Button>
      </ToggleButtonGroup>

      {/* Looping toggle button */}
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
