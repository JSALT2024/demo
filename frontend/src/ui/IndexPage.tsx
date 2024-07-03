import { Box, Link, Sheet, Stack } from "@mui/joy";
import { Link as RouterLink, useLoaderData } from "react-router-dom";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";

export async function indexPageLoader(): Promise<Video[]> {
  const api = BackendApi.current();
  return await api.videos.list();
}

export function IndexPage() {
  const videos = useLoaderData() as Video[];

  return (
    <Box>

      <Sheet sx={{ margin: "10px", padding: "10px" }}>
        <Stack direction="row" spacing={2}>
          <Link component={RouterLink} to="record">Record</Link>
          <Link component={RouterLink} to="upload">Upload</Link>
        </Stack>
      </Sheet>

      Hello world! This is the index page!

      <h2>Videos</h2>

      <ul>
        {videos.map(video => (
          <li>
            <a href="#">{ video.id } / { video.title }</a>
          </li>
        ))}
      </ul>

    </Box>
  );
}
