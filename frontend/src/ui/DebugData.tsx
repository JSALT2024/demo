import { Box, Button, Chip, Typography } from "@mui/joy";
import TheatersIcon from "@mui/icons-material/Theaters";
import { ClipsCollection } from "../api/model/ClipsCollection";
import BugReportIcon from "@mui/icons-material/BugReport";
import { Video } from "../api/model/Video";

export interface DebugDataProps {
  readonly video: Video;
  readonly clipIndex: number;
  readonly clipsCollection: ClipsCollection | null;
}

export function DebugData(props: DebugDataProps) {
  const clipIndex = props.clipIndex;
  const clipsCollection = props.clipsCollection;
  const clip = clipsCollection?.clips?.[clipIndex];
  const video = props.video;

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography
        level="h2"
        sx={{ marginBottom: 2 }}
        startDecorator={<BugReportIcon />}
        endDecorator={
          <Chip variant="soft" startDecorator={<TheatersIcon />}>
            Clip index {clipIndex} of {clipsCollection?.clips?.length}
          </Chip>
        }
      >
        Debug data
      </Typography>

      <Typography level="h3" sx={{ marginTop: 2 }} gutterBottom>
        Clip
      </Typography>
      <Typography level="body-sm" sx={{ whiteSpace: "pre-wrap" }}>
        {JSON.stringify(
          clip,
          (k, v) => (k.startsWith("embedding_") ? "[see above]" : v),
          2,
        )}
      </Typography>

      <Typography level="h3" sx={{ marginTop: 2 }} gutterBottom>
        Video
      </Typography>
      <Typography level="body-sm" sx={{ whiteSpace: "pre-wrap" }}>
        {JSON.stringify(video, null, 2)}
      </Typography>
    </Box>
  );
}
