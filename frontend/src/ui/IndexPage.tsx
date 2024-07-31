import { Box, Typography } from "@mui/joy";
import { Link as RouterLink, useLoaderData } from "react-router-dom";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { Navigation } from "./Navigation";
import logo from "../img/logo.png";
import { VideoList } from "./VideoList";

export async function indexPageLoader(): Promise<Video[]> {
  const api = BackendApi.current();
  return await api.videos.list();
}

export function IndexPage() {
  const videos = useLoaderData() as Video[];

  return (
    <Box>
      <Navigation />
      <Box
        sx={{
          margin: "0 auto",
          maxWidth: "850px",
          paddingTop: 4,
          paddingBottom: "100px",
        }}
      >
        <Box
          sx={{ display: "flex", justifyContent: "center", paddingBottom: 4 }}
        >
          <img src={logo} width={180} />
        </Box>
        <Typography level="h1">Sign LLaVA Demo</Typography>
        <Typography level="body-md">
          This the demonstration application for the Sign LLaVA model - a
          machine translation system developed to translate videos containing an
          American Sign Language signer to english text using the LLaMa large
          language model.
        </Typography>
        <VideoList videos={videos} />
      </Box>
    </Box>
  );
}
