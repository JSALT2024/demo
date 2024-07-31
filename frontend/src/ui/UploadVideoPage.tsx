import { ChangeEvent, useState } from "react";
import { Box, Button } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Navigation } from "./Navigation";
import { useNavigate } from "react-router-dom";

export function UploadVideoPage() {
  const navigate = useNavigate();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState<boolean>(false);

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files === null) {
      return;
    }

    const file: File = e.target.files[0];
    setSelectedFile(file);
  }

  async function onFileUpload() {
    if (selectedFile === null) {
      return;
    }

    const api = BackendApi.current();
    setIsUploading(true);
    const videoId = await api.videos.upload(
      selectedFile.slice(0, selectedFile.size),
      selectedFile.name,
      selectedFile.type,
    );
    navigate(`/videos/${videoId}`);
  }

  return (
    <Box>
      <Navigation />
      <Box sx={{ margin: "0 auto", maxWidth: "850px", paddingBottom: "100px" }}>
        <h2>Upload video file</h2>

        <input type="file" onChange={onFileChange} />

        <Button loading={isUploading} onClick={onFileUpload}>
          Upload
        </Button>

        <p style={{ marginTop: "100px" }}>
          This page is kinda ugly, I know... Not enough time.
        </p>
      </Box>
    </Box>
  );
}
