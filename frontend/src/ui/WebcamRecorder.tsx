import { Box, Button, Stack } from "@mui/joy";
import { useRef, useState } from "react";

export interface WebcamRecorderProps {
  /**
   * Triggered whenever an entire video is recorded or forgotten
   */
  onChange: (video: Blob | null) => void,
}

export function WebcamRecorder(props: WebcamRecorderProps) {

  // TODO: handle errors and exceptions!

  // the video preview element reference
  const previewRef = useRef<HTMLVideoElement | null>(null);
  
  // holds the media stream we record from
  const [mediaStream, setMediaStream] = useState<MediaStream | null>(null);
  
  // recorder instance that exists when recording is in progress
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );

  // recorded chunks; represent the recorded video
  const [chunks, setChunks] = useState<Blob[]>([]);

  // is the stream running?
  const streamExists = (mediaStream !== null);

  // is the recording in progress?
  const isRecording = (mediaRecorder !== null);

  // is there a recorded video?
  const hasRecordedVideo = (!isRecording && chunks.length > 0);

  // how many bytes have been recorded so far
  const recordedBytes = chunks.map(c => c.size).reduce((a, b) => a + b, 0);

  /**
   * Start the media stream (asks the user for camera access)
   */
  async function startStream() {
    if (previewRef.current === null) {
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    setMediaStream(stream);

    const preview = previewRef.current;
    preview.srcObject = stream;
    preview.autoplay = true;
    preview.muted = true;
  }

  /**
   * Releases the media stream
   */
  function stopStream() {
    if (mediaStream === null) {
      return;
    }
    if (previewRef.current === null) {
      return;
    }

    // do nothing if recording in progress
    if (isRecording) {
      return;
    }

    mediaStream.getTracks().forEach(t => t.stop());
    setMediaStream(null);

    const preview = previewRef.current;
    preview.srcObject = null;
  }

  function startRecording() {
    if (mediaStream === null) return;

    const rec = new MediaRecorder(mediaStream);
    
    rec.addEventListener("dataavailable", (e: BlobEvent) => {
      // append the new chunk to the list
      setChunks((_chunks) => [..._chunks, e.data]);
    });

    // start recording
    rec.start(1_000); // flush every 1 second

    // start recording and clear chunks
    setMediaRecorder(rec);
    setChunks([]);
  }

  function stopRecording() {
    if (mediaRecorder === null) {
      return;
    }

    // stop the recording
    mediaRecorder.stop();

    // compose the video from chunks
    const completeVideo = new Blob(chunks, { type: mediaRecorder.mimeType });
    
    // emit the video upwards
    props.onChange(completeVideo);

    // update react state to reflect the stopping
    setMediaRecorder(null);
  }

  function forgetRecordedVideo() {
    if (!hasRecordedVideo) {
      return;
    }
    
    setChunks([]);
    props.onChange(null);
  }

  return (
    <Box>
      <p>Webcam Recorder</p>

      <pre>{ JSON.stringify({
        hasStream: streamExists,
        isRecording,
        hasRecording: hasRecordedVideo,
        recordedBytes,
        chunks: chunks.length,
      }, null, 2) }</pre>

      <Stack direction="row" spacing={2}>
        <Button
          disabled={streamExists}
          onClick={startStream}
        >
          Start stream
        </Button>

        <Button
          disabled={!streamExists || isRecording}
          onClick={stopStream}
        >
          Stop stream
        </Button>

        <Button
          disabled={!streamExists}
          color="danger"
          onClick={() => isRecording ? stopRecording() : startRecording()}
        >
          { isRecording ? "Stop recording" : "Start recording" }
        </Button>

        <Button
          disabled={!hasRecordedVideo}
          onClick={forgetRecordedVideo}
        >
          Forget video
        </Button>
      </Stack>

      { isRecording && (<p></p>)}

      <video ref={previewRef} width={512} style={{ border: "2px solid black" }} />
    </Box>
  );
}