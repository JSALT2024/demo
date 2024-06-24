import { createHashRouter } from "react-router-dom";
import { IndexPage } from "./ui/IndexPage";

export const router = createHashRouter([
  {
    index: true,
    element: <IndexPage />,
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
