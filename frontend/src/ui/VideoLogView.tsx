import { Box, Sheet, Typography } from "@mui/joy";
import { useEffect, useRef } from "react";
import { BackendApi } from "../api/BackendApi";
import ReceiptLongIcon from "@mui/icons-material/ReceiptLong";

export interface VideoLogViewProps {
  readonly videoId: string;
}

export function VideoLogView(props: VideoLogViewProps) {
  const preElementRef = useRef<HTMLPreElement | null>(null);

  useEffect(() => {
    const api = BackendApi.current();
    const logFollower = api.videos.followLog(props.videoId, (nextLine) => {
      if (preElementRef.current === null) return;
      const pre = preElementRef.current;
      const parent = pre.parentElement!;
      pre.append(nextLine);
      parent.scrollTo(0, parent.scrollHeight);
    });
    logFollower.startFollowing();
    return () => {
      logFollower.close();
    };
  }, [props.videoId]);

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography
        level="h2"
        sx={{ marginBottom: 2 }}
        startDecorator={<ReceiptLongIcon />}
      >
        Processing log
      </Typography>

      <Sheet
        variant="outlined"
        sx={{ height: "300px", overflowY: "scroll", padding: 1 }}
      >
        <pre
          ref={preElementRef}
          style={{
            margin: 0,
            whiteSpace: "pre-wrap",
          }}
        ></pre>
      </Sheet>
    </Box>
  );
}
