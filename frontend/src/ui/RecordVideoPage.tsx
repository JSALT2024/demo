import { Box, Button } from "@mui/joy";
import { WebcamRecorder } from "./WebcamRecorder";
import { useState } from "react";
import { BackendApi } from "../api/BackendApi";
import { Navigation } from "./Navigation";
import { useNavigate } from "react-router-dom";

export function RecordVideoPage() {
  const navigate = useNavigate();

  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);

  const [isUploading, setIsUploading] = useState<boolean>(false);

  async function uploadVideo() {
    if (videoBlob === null) {
      return;
    }

    const api = BackendApi.current();
    setIsUploading(true);
    const videoId = await api.videos.upload(
      videoBlob,
      "recorded-video",
      videoBlob.type, // for recording, the mime type is stored here
    );
    navigate(`/videos/${videoId}`);
  }

  return (
    <Box>
      <Navigation />
      <Box sx={{ margin: "0 auto", maxWidth: "850px", paddingBottom: "100px" }}>
        <h2>Record video file</h2>
        <WebcamRecorder onChange={setVideoBlob} />
        <hr />
        <Button
          loading={isUploading}
          disabled={videoBlob === null}
          onClick={uploadVideo}
        >
          Upload and process video
        </Button>
      </Box>
    </Box>
  );
}
