import { Box, Link, Sheet, Stack } from "@mui/joy";
import { Link as RouterLink } from "react-router-dom";
import logo from "../img/logo.png";

export function Navigation() {
  return (
    <Sheet
      variant="outlined"
      sx={{ padding: 1, marginBottom: 1, borderWidth: "0 0 1px 0" }}
    >
      <Stack direction="row" spacing={2} sx={{ px: 2 }}>
        <Link component={RouterLink} to="/">
          <img src={logo} width={36} />
        </Link>
        <Link component={RouterLink} to="/">
          Videos
        </Link>
        <Link component={RouterLink} to="/record">
          Record
        </Link>
        <Link component={RouterLink} to="/upload">
          Upload
        </Link>
      </Stack>
    </Sheet>
  );
}
