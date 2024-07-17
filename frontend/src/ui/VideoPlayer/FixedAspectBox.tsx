import { Box } from "@mui/joy";
import { SxProps } from "@mui/joy/styles/types";

export interface FixedAspectBoxProps {
  readonly sx?: SxProps;
  readonly aspectRatio?: number;
  readonly children?: any;
}

export function FixedAspectBox(props: FixedAspectBoxProps) {
  const percentage = 100 / (props.aspectRatio || 1);

  return (
    <Box sx={{ position: "relative", display: "block", ...props.sx }}>
      
      {/* The stretcher element */}
      <Box sx={{ position: "relative", paddingTop: percentage + "%" }} />
      
      {/* The content wrapper */}
      <Box sx={{
        position: "absolute",
        left: 0,
        top: 0,
        right: 0, 
        bottom: 0,
        overflow: "hidden",
      }}>

        {/* Content */}
        { props.children }
      </Box>
    </Box>
  );
}