import { Box, Button } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { VideoPlayer } from "./VideoPlayer/VideoPlayer";
import { FrameGeometry } from "../api/model/FrameGeometry";

interface VideoPageLoaderData {
  readonly video: Video;
  readonly videoBlob: Blob;
  readonly videoBlobUrl: string;
  readonly frameGeometries: FrameGeometry[];
}

export async function videoPageLoader({ params }): Promise<VideoPageLoaderData> {
  // fetch the video record
  const api = BackendApi.current();
  const video = await api.videos.get(params.videoId);

  // fetch the video file
  const videoFileUrl = video.normalized_file
    ? api.videos.getNormalizedVideoFileUrl(video.id)
    : api.videos.getUploadedVideoFileUrl(video.id);
  const videoBlob = await (await fetch(videoFileUrl)).blob();
  const videoBlobUrl = URL.createObjectURL(videoBlob);

  // fetch the geometry file
  const geometryFileUrl = api.videos.getGeometryUrl(video.id)
  const frameGeometries = await (
    await fetch(geometryFileUrl)
  ).json() as FrameGeometry[];

  return {
    video,
    videoBlob,
    videoBlobUrl,
    frameGeometries,
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
        videoBlob={data.videoBlob}
        videoBlobUrl={data.videoBlobUrl}
        frameGeometries={data.frameGeometries}
      />

      <pre>{ JSON.stringify(data.video, null, 2) }</pre>

    </Box>
  );
}