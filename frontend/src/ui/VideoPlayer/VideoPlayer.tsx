import { Box, Sheet, Stack, Typography } from "@mui/joy";
import { useRef } from "react";
import { VideoFile } from "../../api/model/Video";
import { VideoNavigation } from "./VideoNavigation";
import { useFrameChangeEvent, useVideoPlayerController } from "./VideoPlayerController";
import { VideoPreview } from "./VideoPreview";
import { FrameGeometry } from "../../api/model/FrameGeometry";
import { VideoCrops } from "../../api/model/VideoCrops";
import { CropView } from "./CropView";

export interface VideoPlayerProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob | null;
  readonly frameGeometries: FrameGeometry[] | null;
  readonly videoCrops: VideoCrops | null;
}

export function VideoPlayer(props: VideoPlayerProps) {
  const videoPlayerController = useVideoPlayerController({
    videoFile: props.videoFile,
  });

  const frameNumberRef = useRef<HTMLPreElement | null>(null);

  function onFrameChange(frameIndex: number) {
    // update the frame number
    if (frameNumberRef.current !== null) {
      frameNumberRef.current.innerHTML = String(frameIndex);
    }
  }

  // listening for frame changes
  useFrameChangeEvent(
    videoPlayerController,
    e => onFrameChange(e.frameIndex),
    [], // dependencies of the handler function
  );
  
  return (
    <Sheet variant="outlined" sx={{ borderRadius: "5px", overflow: "hidden" }}>
      <Box sx={{ display: "flex", flexDirection: "row" }}>
        <VideoPreview
          sx={{ width: "50%" }}
          videoBlob={props.videoBlob}
          videoPlayerController={videoPlayerController}
          frameGeometries={props.frameGeometries}
        />
        <Box
          sx={{
            display: "flex",
            flexDirection: "column",
            flexGrow: "1",
            padding: 2
          }}
        >
          <Typography level="h4" gutterBottom>
            Frame <span ref={frameNumberRef}>0</span>, Clip <span>XYZ</span>
          </Typography>
          <Stack direction="row" spacing={1}>
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Right Hand"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.right_hand || null}
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Face"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.face || null}
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Left Hand"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.left_hand || null}
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="MAE"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.images || null}
            />
          </Stack>
          <Typography level="body-xs" gutterBottom sx={{ marginTop: 2 }}>
            Clip Translation
          </Typography>
          <Sheet
            sx={{
              flexGrow: 1,
              position: "relative",
              background: "var(--joy-palette-neutral-100)",
            }}
          >
            <Typography
              level="body-lg"
              sx={{
                position: "absolute",
                top: "0px",
                bottom: "0px",
                left: "0px",
                right: "0px",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                textAlign: "center",
                padding: 2,
              }}
            >
              Lorem ipsum dolor sit amet...
            </Typography>
          </Sheet>
        </Box>
      </Box>
      <VideoNavigation videoPlayerController={videoPlayerController} />
    </Sheet>
  );
}
