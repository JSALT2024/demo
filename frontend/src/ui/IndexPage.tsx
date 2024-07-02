import { Box } from "@mui/joy";
import { ChangeEvent, useState } from "react";
import { WebcamRecorder } from "./WebcamRecorder";

export function IndexPage() {

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
      Hello world! This is the index page!

      <div>
        <input type="file" onChange={onFileChange} />
        <button onClick={onFileUpload}>
          Upload!
        </button>
      </div>
    </Box>
  );
}
