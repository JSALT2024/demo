import { Box, Button, Typography } from "@mui/joy";
import VideoSettingsIcon from "@mui/icons-material/VideoSettings";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import PrecisionManufacturingIcon from "@mui/icons-material/PrecisionManufacturing";
import DeleteIcon from "@mui/icons-material/Delete";
import { useNavigate } from "react-router-dom";

export interface VideoManagementProps {
  readonly video: Video;
}

export function VideoManagement(props: VideoManagementProps) {
  const navigate = useNavigate();

  const video = props.video;

  async function reprocessVideo() {
    const api = BackendApi.current();
    await api.videos.reprocess(video.id);
    window.location.reload();
  }

  async function deleteVideo() {
    const api = BackendApi.current();
    await api.videos.delete(video.id);
    navigate("/");
  }

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography
        level="h2"
        sx={{ marginBottom: 2 }}
        startDecorator={<VideoSettingsIcon />}
      >
        Video management
      </Typography>

      <Typography level="h3">Re-processing</Typography>
      <Typography level="body-md">
        Clicking the re-processing button will run all of the processing that
        usually happens when the video is uploaded. It clears the processing log
        and runs all stages. Once to processing according to the log finishes,
        refresh the page to fetch the new data to your browser.
      </Typography>
      <Button
        sx={{ marginTop: 1, marginBottom: 2 }}
        onClick={() => reprocessVideo()}
        startDecorator={<PrecisionManufacturingIcon />}
      >
        Re-process the video
      </Button>

      <Typography level="h3">Cleaning up</Typography>
      <Typography level="body-md">
        You can delete the video by clicking the button below.
      </Typography>
      <Button
        sx={{ marginTop: 1 }}
        color="danger"
        onClick={() => deleteVideo()}
        startDecorator={<DeleteIcon />}
      >
        Delete video
      </Button>
    </Box>
  );
}
