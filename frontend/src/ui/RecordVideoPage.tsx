import { Box, Button } from "@mui/joy";
import { WebcamRecorder } from "./WebcamRecorder";
import { useState } from "react";
import { BackendApi } from "../api/BackendApi";

export function RecordVideoPage() {
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);

  async function uploadVideo() {
    if (videoBlob === null) {
      return;
    }

    const api = BackendApi.current();
    await api.videos.upload(videoBlob, "recorded-video");
  }

  return (
    <Box>
      <h2>Record video file</h2>
      <WebcamRecorder onChange={setVideoBlob} />
      <hr />
      <Button disabled={videoBlob === null} onClick={uploadVideo}>
        Upload and process video
      </Button>
    </Box>
  );
}
