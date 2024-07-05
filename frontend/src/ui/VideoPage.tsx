import { Box } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { useLoaderData } from "react-router-dom";

export async function videoPageLoader({ params }): Promise<Video> {
  const api = BackendApi.current();
  return await api.videos.get(params.videoId);
}

export function VideoPage() {
  const api = BackendApi.current();
  const video = useLoaderData() as Video;

  return (
    <Box>
      Video detail!
      <pre>{ JSON.stringify(video, null, 2) }</pre>

      <video
        src={api.videos.getVideoFileUrl(video.id).toString()}
        muted
        width={512}
        controls
      ></video>

    </Box>
  );
}