import { Sheet } from "@mui/joy";
import { VideoNavigation } from "./VideoNavigation";
import { VideoPlayerController } from "./VideoPlayerController";
import { ClipsCollection } from "../../api/model/ClipsCollection";
import { useCallback, useEffect, useRef } from "react";

export interface FloatingVideoNavigationProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly clipsCollection: ClipsCollection | null;
}

const APPEAR_AFTER_PX = 100;

export function FloatingVideoNavigation(props: FloatingVideoNavigationProps) {
  const sheetRef = useRef<HTMLElement | null>(null);

  const handleScroll = useCallback(() => {
    if (sheetRef.current === null) return;
    if (window.scrollY > APPEAR_AFTER_PX) {
      sheetRef.current.style.transform = "translateY(0%)";
    } else {
      sheetRef.current.style.transform = "translateY(100%)";
    }
  }, []);

  useEffect(() => {
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  });

  return (
    <Sheet
      // ref={sheetRef} just such that typescript is fine:
      {...({ ref: sheetRef } as any)}
      // (the issue is that MUI is missing the type definition but it works fine)
      variant="outlined"
      sx={{
        display: "block",
        zIndex: 100,
        position: "fixed",
        bottom: 0,
        left: 0,
        width: "100%",
        borderBottom: "none",
        borderLeft: "none",
        borderRight: "none",
        transition: "transform 200ms",
        transform: "translateY(100%)",
        boxShadow: "0 0 3px 0 rgba(0, 0, 0, 0.1)",
      }}
    >
      <VideoNavigation
        videoPlayerController={props.videoPlayerController}
        clipsCollection={props.clipsCollection}
      />
    </Sheet>
  );
}
