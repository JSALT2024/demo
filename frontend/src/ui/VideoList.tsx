import { Box, Typography, Grid } from "@mui/joy";
import { Video } from "../api/model/Video";
import { VideoCard } from "./VideoCard";

export interface VideoListProps {
  readonly videos: Video[];
}

export function VideoList(props: VideoListProps) {
  const sortedVideos = [...props.videos].sort((a, b) =>
    a.created_at.localeCompare(b.created_at),
  );

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography level="h2" sx={{ marginBottom: 2 }}>
        Uploaded Videos
      </Typography>

      <Grid container spacing={2}>
        {sortedVideos.map((video) => (
          <Grid key={video.id} xs={4} sx={{ display: "flex" }}>
            <VideoCard video={video} sx={{ flexGrow: 1 }} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
