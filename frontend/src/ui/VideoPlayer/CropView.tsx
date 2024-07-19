import { SxProps } from "@mui/joy/styles/types";
import { FixedAspectBox } from "./FixedAspectBox";
import { VideoPlayerController, useFrameChangeEvent } from "./VideoPlayerController";
import { Box, CircularProgress, IconButton, Typography } from "@mui/joy";
import { CSSProperties, useEffect, useRef } from "react";
import VisibilityIcon from "@mui/icons-material/Visibility";
import VisibilityOffIcon from "@mui/icons-material/VisibilityOff";

// https://stackoverflow.com/a/14115340
const EMPTY_IMAGE_URL = "data:image/gif;base64,R0lGODlhAQABAAD/ACwAAAAAAQABAAACADs=";

export interface CropViewProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly cropFrames: Blob[] | null;
  readonly label: string;
  readonly sx?: SxProps;
}

export function CropView(props: CropViewProps) {
  const imgElementRef = useRef<HTMLImageElement | null>(null);

  function onFrameChange(frameIndex: number) {
    if (imgElementRef.current === null) return;

    let blob: Blob | null = null;
    if (props.cropFrames !== null && props.cropFrames[frameIndex]) {
      blob = props.cropFrames[frameIndex];
    }

    // prepare the new URL
    const newCropUrl = (
      blob === null ? EMPTY_IMAGE_URL : URL.createObjectURL(blob)
    );
    
    // remember the old URL
    const oldCropUrl = imgElementRef.current.src;

    // swap the URL
    imgElementRef.current.src = newCropUrl;
    
    // clean up the old URL
    if (oldCropUrl != "" && oldCropUrl !== EMPTY_IMAGE_URL) {
      URL.revokeObjectURL(oldCropUrl);
    }
  }

  // listening for frame changes
  useFrameChangeEvent(
    props.videoPlayerController,
    e => onFrameChange(e.frameIndex),
    [props.cropFrames], // dependencies of the handler function
  );

  // revoking the Blob URL when the component unmounts
  useEffect(() => {
    return () => {
      const oldCropUrl = imgElementRef?.current?.src || "";
      if (oldCropUrl != "" && oldCropUrl !== EMPTY_IMAGE_URL) {
        URL.revokeObjectURL(oldCropUrl);
      }
    }
  }, []);

  const FILL_STYLE: CSSProperties = {
    position: "absolute",
    top: "0%",
    left: "0%",
    width: "100%",
    height: "100%",
  };

  return (
    <Box sx={{ ...props.sx }}>
      <Typography level="body-xs" sx={{ textAlign: "center" }}>
        { props.label }
      </Typography>
      <FixedAspectBox
        aspectRatio={1 / 1}
        sx={{
          // ...props.sx,
          background: "var(--joy-palette-neutral-100)",
          "&:hover": {
            "& .cropViewButton": {
              opacity: 0.8,
            },
            "& .cropViewSpinner": {
              opacity: 0,
            }
          }
        }}
      >
        {/* The image element that renders the crop frame */}
        <img
          ref={imgElementRef}
          style={{ ...FILL_STYLE }}
        />

        {/* Spinner shown when the crops have not been loaded yet */}
        {props.cropFrames === null && (
          <CircularProgress
            className="cropViewSpinner"
            sx={FILL_STYLE} size="sm" variant="solid"
          />
        )}

        {/* Overlay button that toggles landmark visibility in the video */}
        <IconButton
          className="cropViewButton"
          sx={{
            ...FILL_STYLE,
            opacity: 0,
            borderRadius: 0,
          }}
          size="lg"
          variant="plain"
        >
          <VisibilityIcon />
          {/* <VisibilityOffIcon /> */}
        </IconButton>
      </FixedAspectBox>
    </Box>
  );
}