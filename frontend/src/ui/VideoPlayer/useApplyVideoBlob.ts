import { useEffect } from "react";
import { VideoPlayerController } from "./VideoPlayerController";

export interface ApplyVideoBlobProps {
  readonly videoPlayerController: VideoPlayerController;
  readonly videoBlob: Blob | null;
}

/**
 * Sets the video player controller's <video> element's src attribute
 * to the given video Blob instance. Basically just makes sure
 * that object URLs are properly allocated and freed again.
 */
export function useApplyVideoBlob(props: ApplyVideoBlobProps) {
  useEffect(() => {
    if (props.videoPlayerController.videoElementRef.current === null) return;

    // when the video blob is set, create an object URL and
    // assign it to the src attribute. If the blob is null,
    // set the src to emptystring.
    const element = props.videoPlayerController.videoElementRef.current;
    const blobUrl =
      props.videoBlob === null ? "" : URL.createObjectURL(props.videoBlob);
    element.src = blobUrl;

    // when the blob value changes or the componen unmounts, release the
    // object url, unless it was an empty string and remove the src value
    // of the video element
    return () => {
      element.src = "";
      if (blobUrl != "") {
        URL.revokeObjectURL(blobUrl);
      }
    };
  }, [props.videoBlob]);
}
