import { createHashRouter } from "react-router-dom";
import { IndexPage } from "./ui/IndexPage";
import { RecordVideoPage } from "./ui/RecordVideoPage";

export const router = createHashRouter([
  {
    index: true,
    element: <IndexPage />,
  },
  {
    path: "record",
    element: <RecordVideoPage />,
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
