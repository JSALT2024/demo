import { ChangeEvent, useState } from "react";
import { Box } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";

export function UploadVideoPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

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
    await api.videos.upload(
      selectedFile.slice(0, selectedFile.size),
      selectedFile.name,
    );
  }

  return (
    <Box>
      <h2>Upload video file</h2>

      <div>
        <input type="file" onChange={onFileChange} />
        <button onClick={onFileUpload}>Upload!</button>
      </div>
    </Box>
  );
}
