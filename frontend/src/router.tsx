import { createHashRouter } from "react-router-dom";
import { IndexPage, indexPageLoader } from "./ui/IndexPage";
import { RecordVideoPage } from "./ui/RecordVideoPage";
import { UploadVideoPage } from "./ui/UploadVideoPage";
import { VideoPage, videoPageLoader } from "./ui/VideoPage";

export const router = createHashRouter([
  {
    index: true,
    element: <IndexPage />,
    loader: indexPageLoader,
  },
  {
    path: "record",
    element: <RecordVideoPage />,
  },
  {
    path: "upload",
    element: <UploadVideoPage />,
  },
  {
    path: "videos/:videoId",
    element: <VideoPage />,
    loader: videoPageLoader,
  },
  // Example additional pages:
  //
  // {
  //   element: <LegalRoot />,
  //   children: [
  //     {
  //       path: "privacy-policy",
  //       element: <PrivacyPolicyPage />,
  //     },
  //   ],
  // },
]);
