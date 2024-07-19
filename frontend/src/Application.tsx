import { CssBaseline } from "@mui/joy";
import { CssVarsProvider } from "@mui/joy/styles";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { theme } from "./theme";

export function Application() {
  return (
    <CssVarsProvider theme={theme}>
      <CssBaseline />

      <RouterProvider router={router} />
    </CssVarsProvider>
  );
}
