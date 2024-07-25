import { Box, Button, Typography } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";
import { VideoPlayer } from "./VideoPlayer/VideoPlayer";
import { FrameGeometry } from "../api/model/FrameGeometry";
import { VideoCrops } from "../api/model/VideoCrops";
import { useEffect, useState } from "react";
import { ClipsCollection } from "../api/model/ClipsCollection";

interface VideoPageLoaderData {
  readonly video: Video;
}

export async function videoPageLoader({
  params,
}): Promise<VideoPageLoaderData> {
  // fetch only the video record
  const api = BackendApi.current();
  const video = await api.videos.get(params.videoId);
  return {
    video,
  };
}

export function VideoPage() {
  const data = useLoaderData() as VideoPageLoaderData;

  const [normalizedVideoBlob, setNormalizedVideoBlob] = useState<Blob | null>(
    null,
  );
  const [frameGeometries, setFrameGeometries] = useState<
    FrameGeometry[] | null
  >(null);
  const [videoCrops, setVideoCrops] = useState<VideoCrops | null>(null);
  const [clipsCollection, setClipsCollection] =
    useState<ClipsCollection | null>(null);

  // download the heavy video data
  useEffect(() => {
    (async () => {
      const api = BackendApi.current();
      setNormalizedVideoBlob(
        await api.videos.getNormalizedVideoBlob(data.video.id),
      );
      setFrameGeometries(await api.videos.getFrameGeometries(data.video.id));
      setVideoCrops(await api.videos.getCrops(data.video.id));
      setClipsCollection(await api.videos.getClipsCollection(data.video.id));
    })();
  }, [data.video.id]);

  async function reprocessVideo() {
    const api = BackendApi.current();
    await api.videos.reprocess(data.video.id);
  }

  return (
    <Box>
      <Box sx={{ margin: "0 auto", maxWidth: "850px" }}>
        {/* <Typography level="h1" gutterBottom>
          Video Title Goes Here
        </Typography> */}

        {data.video.normalized_file ? (
          <VideoPlayer
            videoFile={data.video.normalized_file}
            videoBlob={normalizedVideoBlob}
            frameGeometries={frameGeometries}
            videoCrops={videoCrops}
            clipsCollection={clipsCollection}
          />
        ) : (
          <Typography level="body-md" color="warning">
            The video has not beed normalized yet, wait and reload the page.
          </Typography>
        )}
      </Box>
      <pre>{JSON.stringify(data.video, null, 2)}</pre>
      <Button onClick={() => reprocessVideo()}>Re-process video</Button>
    </Box>
  );
}
