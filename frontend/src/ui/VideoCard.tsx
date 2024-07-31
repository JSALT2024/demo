import { AspectRatio, Card, CardContent, Link, Typography } from "@mui/joy";
import { BackendApi } from "../api/BackendApi";
import { Video } from "../api/model/Video";
import { Link as RouterLink } from "react-router-dom";
import { SxProps } from "@mui/material";

export interface VideoCardProps {
  readonly video: Video;
  readonly sx?: SxProps;
}

function zpad(value: number, digits: number): string {
  let text = String(value);
  while (text.length < digits) {
    text = "0" + text;
  }
  return text;
}

function formatDuration(seconds?: number): string {
  if (seconds === undefined) return "unknown";
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds - minutes * 60);
  return zpad(minutes, 2) + ":" + zpad(remainingSeconds, 2);
}

export function VideoCard(props: VideoCardProps) {
  const video = props.video;
  const api = BackendApi.current();

  return (
    <Card
      variant="outlined"
      sx={{
        ...props.sx,
        "&:hover": {
          boxShadow: "md",
          borderColor: "neutral.outlinedHoverBorder",
        },
      }}
    >
      <AspectRatio ratio={16 / 9}>
        <img
          src={String(api.videos.getThumbnailUrl(video.id))}
          loading="lazy"
        />
        <Typography
          level="body-sm"
          sx={{
            display: "block",
            position: "absolute",
            top: "8px",
            right: "10px",
            fontWeight: 700,
            color: "rgba(255, 255, 255, 0.9)",
            textShadow: "0 0 2px black",
          }}
        >
          {formatDuration(video.normalized_file?.duration_seconds)}
        </Typography>
      </AspectRatio>
      <CardContent>
        <Typography level="title-md" id="card-description">
          {video.title}
        </Typography>
        <Typography level="body-xs">
          {new Date(video.created_at).toLocaleString()}
        </Typography>
        <Typography level="body-xs" aria-describedby="card-description" mb={1}>
          <Link
            overlay
            underline="none"
            component={RouterLink}
            to={"/videos/" + video.id}
            sx={{ color: "text.tertiary" }}
          >
            {video.id}
          </Link>
        </Typography>
      </CardContent>
    </Card>
  );
}
