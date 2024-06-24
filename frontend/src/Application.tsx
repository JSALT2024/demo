import { CssBaseline } from "@mui/joy";
import { CssVarsProvider } from "@mui/joy/styles";
import { RouterProvider } from "react-router-dom";
import { router } from "./router";
import { StrictMode } from "react";
import { theme } from "./theme";

export function Application() {
  return (
    <CssVarsProvider theme={theme}>
      <CssBaseline />

      <StrictMode>
        <RouterProvider router={router} />
      </StrictMode>
    </CssVarsProvider>
  );
}
