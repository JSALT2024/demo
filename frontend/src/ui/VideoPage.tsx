import { Box, Button, Typography } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { VideoPlayer } from "./VideoPlayer/VideoPlayer";
import { FrameGeometry } from "../api/model/FrameGeometry";
import { VideoCrops } from "../api/model/VideoCrops";
import { useEffect, useState } from "react";

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
  const frameGeometries = await api.videos.getFrameGeometries(video.id);

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

  const [videoCrops, setVideoCrops] = useState<VideoCrops | null>(null);

  // download video crops
  useEffect(() => {
    (async () => {
      const api = BackendApi.current();
      const crops = await api.videos.getCrops(data.video.id)
      setVideoCrops(crops);
    })();
  }, [data.video.id]);

  async function reprocessVideo() {
    const api = BackendApi.current();
    await api.videos.reprocess(data.video.id);
  }

  return (
    <Box>
      Video detail!

      <Button onClick={() => reprocessVideo()}>Re-process video</Button>

      <Box sx={{ margin: "0 auto", maxWidth: "850px" }}>

        <Typography level="h1" gutterBottom>
          Video Title Goes Here
        </Typography>

        <VideoPlayer
          videoFile={video_file}
          videoBlob={data.videoBlob}
          videoBlobUrl={data.videoBlobUrl}
          frameGeometries={data.frameGeometries}
          videoCrops={videoCrops}
        />
      </Box>

      <pre>{ JSON.stringify(data.video, null, 2) }</pre>

    </Box>
  );
}