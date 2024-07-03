import { ChangeEvent, useState } from "react";
import { Box } from "@mui/joy";

export function UploadVideoPage() {

  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  function onFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files === null) {
      return;
    }

    const file: File = e.target.files[0];
    setSelectedFile(file);
  }

  function onFileUpload() {
    if (selectedFile === null) {
      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile.slice(0, selectedFile.size),
      selectedFile.name
    );

    fetch("http://localhost:1817/upload", {
      method: "POST",
      body: formData,
    });
  }

  return (
    <Box>
      <h2>Upload video file</h2>

      <div>
        <input type="file" onChange={onFileChange} />
        <button onClick={onFileUpload}>
          Upload!
        </button>
      </div>
    </Box>
  );
}