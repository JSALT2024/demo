import { Box, Button } from "@mui/joy";
import { WebcamRecorder } from "./WebcamRecorder";
import { useState } from "react";

export function RecordVideoPage() {
  const [videoBlob, setVideoBlob] = useState<Blob | null>(null);

  function uploadVideo() {
    if (videoBlob === null) {
      return;
    }

    // TODO
    // Create a dummy download link for now
    const chunkUrl = URL.createObjectURL(videoBlob);
    const a = document.createElement("a");
    a.innerText = "Click this link to download the recorded video";
    a.href = chunkUrl;
    document.body.appendChild(a);
  }

  return (
    <Box>
      <h2>Record video file</h2>
      <WebcamRecorder
        onChange={setVideoBlob}
      />
      <hr />
      <Button
        disabled={videoBlob === null}
        onClick={uploadVideo}
      >
        Upload and process video
      </Button>
    </Box>
  );
}