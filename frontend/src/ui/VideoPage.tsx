import { Box, Slider, Button } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { VideoPlayer } from "./VideoPlayer/VideoPlayer";

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

  async function reprocessVideo() {
    const api = BackendApi.current();
    await api.videos.reprocess(data.video.id);
  }

  return (
    <Box>
      Video detail!

      <Button onClick={() => reprocessVideo()}>Re-process video</Button>

      <VideoPlayer
        videoFile={video_file}
        videoBlob={data.blob}
        videoBlobUrl={data.blobUrl}
      />

      <pre>{ JSON.stringify(data.video, null, 2) }</pre>

    </Box>
  );
}