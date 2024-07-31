import { Box, Sheet, Stack, Typography } from "@mui/joy";
import { useRef, useState } from "react";
import { VideoFile } from "../../api/model/Video";
import { VideoNavigation } from "./VideoNavigation";
import {
  useFrameChangeEvent,
  useVideoPlayerController,
} from "./VideoPlayerController";
import { VideoPreview } from "./VideoPreview";
import { FrameGeometry } from "../../api/model/FrameGeometry";
import { VideoCrops } from "../../api/model/VideoCrops";
import { CropView } from "./CropView";
import { ClipsCollection } from "../../api/model/ClipsCollection";
import { FloatingVideoNavigation } from "./FloatingVideoNavigation";

export interface VideoPlayerProps {
  readonly videoFile: VideoFile;
  readonly videoBlob: Blob | null;
  readonly frameGeometries: FrameGeometry[] | null;
  readonly videoCrops: VideoCrops | null;
  readonly clipsCollection: ClipsCollection | null;
  readonly onClipIndexChange?: (clipIndex: number) => void;
}

/**
 * Returns the font size to use based ony the length of the translated text
 */
function fontSizeFromTranslationLength(length: number): string {
  let size: number = 24;
  if (length > 50) size = 20;
  if (length > 150) size = 18;
  if (length > 300) size = 14;
  if (length > 500) size = 12;
  if (length > 700) size = 10;
  return String(size) + "px";
}

export function VideoPlayer(props: VideoPlayerProps) {
  const videoPlayerController = useVideoPlayerController({
    videoFile: props.videoFile,
  });

  const frameNumberRef = useRef<HTMLSpanElement | null>(null);
  const clipNumberRef = useRef<HTMLSpanElement | null>(null);
  const [clipTranslation, setClipTranslation] = useState<string | null>(null);

  const lastExportedClipIndexRef = useRef<number>(0);

  function onFrameChange(frameIndex: number) {
    // update the frame number
    if (frameNumberRef.current !== null) {
      frameNumberRef.current.innerHTML = String(frameIndex);
    }

    // the rest of the function updates clip-related data
    if (props.clipsCollection === null) return;

    let clipIndex = props.clipsCollection.clip_index_lookup[frameIndex];
    let clip = props.clipsCollection.clips[clipIndex];

    // update the clip number
    if (clipNumberRef.current !== null) {
      clipNumberRef.current.innerHTML = String(clipIndex);
    }

    // export clip index
    if (lastExportedClipIndexRef.current !== clipIndex) {
      lastExportedClipIndexRef.current = clipIndex;
      props.onClipIndexChange?.(clipIndex);
    }

    // update the displayed translation
    if (clipTranslation !== clip.translation_result) {
      setClipTranslation(clip.translation_result);
    }
  }

  // listening for frame changes
  useFrameChangeEvent(
    videoPlayerController,
    (e) => onFrameChange(e.frameIndex),
    [props.clipsCollection, clipTranslation], // dependencies of the handler
  );

  return (
    <Sheet variant="outlined" sx={{ borderRadius: "5px", overflow: "hidden" }}>
      <Box
        sx={{
          display: "flex",
          flexDirection: "row",
          borderBottom: "1px solid var(--joy-palette-neutral-300)",
        }}
      >
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
            padding: 2,
          }}
        >
          <Typography level="h4" gutterBottom>
            Frame <span ref={frameNumberRef}>0</span>, Clip{" "}
            <span ref={clipNumberRef}>0</span>
          </Typography>
          <Stack direction="row" spacing={1}>
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Right Hand"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.right_hand || null}
              overlayVisible={videoPlayerController.overlayRightHand}
              toggleOverlay={() =>
                videoPlayerController.setOverlayRightHand((v) => !v)
              }
              color="yellow"
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Face"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.face || null}
              overlayVisible={videoPlayerController.overlayFace}
              toggleOverlay={() =>
                videoPlayerController.setOverlayFace((v) => !v)
              }
              color="tomato"
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="Left Hand"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.left_hand || null}
              overlayVisible={videoPlayerController.overlayLeftHand}
              toggleOverlay={() =>
                videoPlayerController.setOverlayLeftHand((v) => !v)
              }
              color="cyan"
            />
            <CropView
              sx={{ width: "32px", flexGrow: 1 }}
              label="MAE"
              videoPlayerController={videoPlayerController}
              cropFrames={props.videoCrops?.images || null}
              overlayVisible={videoPlayerController.overlayPose}
              toggleOverlay={() =>
                videoPlayerController.setOverlayPose((v) => !v)
              }
              color="lime"
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
                overflow: "hidden",
                fontSize: fontSizeFromTranslationLength(
                  clipTranslation ? clipTranslation.length : 0,
                ),
              }}
            >
              {String(clipTranslation)}
            </Typography>
          </Sheet>
        </Box>
      </Box>
      <VideoNavigation
        videoPlayerController={videoPlayerController}
        clipsCollection={props.clipsCollection}
      />
      <FloatingVideoNavigation
        videoPlayerController={videoPlayerController}
        clipsCollection={props.clipsCollection}
      />
    </Sheet>
  );
}
