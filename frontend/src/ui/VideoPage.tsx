import { Box, Slider, Button } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { useRef, useState } from "react";

interface VideoPageLoaderData {
  readonly video: Video;
  readonly blob: Blob;
  readonly blobUrl: string;
}

export async function videoPageLoader({ params }): Promise<VideoPageLoaderData> {
  // fetch the video record
  const api = BackendApi.current();
  const video = await api.videos.get(params.videoId);

  // fetch the video file
  const fileUrl = api.videos.getUploadedVideoFileUrl(video.id);
  const response = await fetch(fileUrl);
  const blob = await response.blob();
  const blobUrl = URL.createObjectURL(blob);

  return {
    video,
    blob,
    blobUrl,
  };
}

export function VideoPage() {
  const data = useLoaderData() as VideoPageLoaderData;
  const video_file = data.video.uploaded_file; // TODO: should be normalized file

  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const [frameIndex, setFrameIndex] = useState<number>(0);

  function handleSliderChange(event: Event, newValue: number) {
    if (videoElementRef.current === null) return;
    const player = videoElementRef.current;

    // console.log(player.duration)
    player.currentTime = video_file.duration_seconds * (
      newValue / video_file.frame_count
    );
    setFrameIndex(newValue);
  }

  return (
    <Box>
      Video detail!
      <pre>{ JSON.stringify(data.video, null, 2) }</pre>

      <video
        ref={videoElementRef}
        src={data.blobUrl}
        muted
        width={512}
        controls

        onTimeUpdate={(e) => {
          // console.log(videoElementRef.current?.currentTime);
          setFrameIndex(
            videoElementRef.current?.currentTime / video_file.duration_seconds
            * video_file.frame_count
          )
        }}
      ></video>

      <pre>Video Element: { String(videoElementRef.current) }</pre>

      <Button
        onClick={() => { videoElementRef.current?.load() }}
      >
        Load
      </Button>

      <Box sx={{ margin: "24px" }}>
        <Slider
          defaultValue={0}
          min={0}
          max={video_file.frame_count}
          step={1}
          marks
          valueLabelDisplay="on"
          value={frameIndex}
          onChange={handleSliderChange}
        />
      </Box>

    </Box>
  );
}