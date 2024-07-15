import { Box, Slider, Button } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { SyntheticEvent, useRef, useState } from "react";
import { VideoRenderer } from "./VideoRenderer";

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
  const fileUrl = video.normalized_file
    ? api.videos.getNormalizedVideoFileUrl(video.id)
    : api.videos.getUploadedVideoFileUrl(video.id);
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
  const video_file = data.video.normalized_file || data.video.uploaded_file;

  const videoElementRef = useRef<HTMLVideoElement | null>(null);
  const [frameIndex, setFrameIndex] = useState<number>(0);

  // function handleSliderChange(event: Event, newValue: number) {
  //   if (videoElementRef.current === null) return;
  //   const player = videoElementRef.current;

  //   // console.log(player.duration)
  //   player.currentTime = video_file.duration_seconds * (
  //     newValue / video_file.frame_count
  //   );
  //   setFrameIndex(newValue);
  // }

  // function handleCanPlay(e: SyntheticEvent<HTMLVideoElement>) {
  //   if (videoElementRef.current === null) return;
  //   const v = videoElementRef.current;

  //   const time = v.currentTime - drift;
  //     const frame = Math.floor(time / FRAME);
  //     currentFrame = frame;
  //     nextFrame = frame + 1;
  //     nextFrameTime = nextFrame * FRAME;
  //     if (paintCount) {
  //       lastPaintCount = v[paintCount];
  //     }
  //     console.log("seeked");
  // }

  function handleSeeked(e: SyntheticEvent<HTMLVideoElement>) {
    if (videoElementRef.current === null) return;
  }

  return (
    <Box>
      Video detail!

      <VideoRenderer
        videoFile={video_file}
        videoBlob={data.blob}
        videoBlobUrl={data.blobUrl}
      />

      <pre>{ JSON.stringify(data.video, null, 2) }</pre>

      <video
        ref={videoElementRef}
        src={data.blobUrl}
        muted
        width={512}
        controls

        // onTimeUpdate={(e) => {
        //   setFrameIndex(
        //     videoElementRef.current?.currentTime / video_file.duration_seconds
        //     * video_file.frame_count
        //   )
        // }}

        // onCanPlay={handleCanPlay}
        // onSeeked={handleSeeked}
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
          // onChange={handleSliderChange}
        />
      </Box>

    </Box>
  );
}