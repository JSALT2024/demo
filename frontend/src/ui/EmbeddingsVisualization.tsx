import { Box, Checkbox, Chip, Typography } from "@mui/joy";
import { ClipsCollection } from "../api/model/ClipsCollection";
import TheatersIcon from "@mui/icons-material/Theaters";
import BubbleChartIcon from "@mui/icons-material/BubbleChart";
import * as d3 from "d3";
import { Stack } from "@mui/system";
import { useState } from "react";

export interface EmbeddingsVisualizationProps {
  readonly clipIndex: number;
  readonly clipsCollection: ClipsCollection;
}

function prettifyToken(token: string) {
  return String(token).replace("Ġ", "");
}

function codifyToken(token: string) {
  return '"' + token + '"';
}

interface TokenCount {
  readonly token: string;
  readonly count: number;
  readonly encoder: string;
}

function countNeighbors(tokens: string[], encoder: string): TokenCount[] {
  const countDict = {};
  for (const token of tokens) {
    if (token in countDict) {
      countDict[token] += 1;
    } else {
      countDict[token] = 1;
    }
  }
  return Object.keys(countDict).map((token) => ({
    token: token,
    count: countDict[token],
    encoder: encoder,
  }));
}

function renderBubbleChart(data: TokenCount[]): SVGSVGElement {
  // Based on:
  // https://observablehq.com/@d3/bubble-chart/2?intent=fork
  const width = 600;
  const height = width;
  const margin = 1;
  const name = (d) => prettifyToken(d.token);
  const names = (d) => [prettifyToken(d.token), d.encoder];

  const maxCount = data.map((d) => d.count).reduce((a, b) => Math.max(a, b), 1);

  // Specify the number format for values.
  const format = d3.format(",d");

  // Create a categorical color scale.
  // const color = d3.scaleOrdinal(d3.schemeTableau10);
  const maeColor = d3.scaleLinear([0, maxCount], ["#EDF5FD", "#97C3F0"]);
  const dinoColor = d3.scaleLinear([0, maxCount], ["#F6FEF6", "#51BC51"]);
  const s2vColor = d3.scaleLinear([0, maxCount], ["#FEF6F6", "#E47474"]);

  function color(d: TokenCount) {
    if (d.encoder == "MAE") return maeColor(d.count);
    if (d.encoder == "DINO") return dinoColor(d.count);
    if (d.encoder == "S2V") return s2vColor(d.count);
  }

  // Create the pack layout.
  const pack = d3
    .pack()
    .size([width - margin * 2, height - margin * 2])
    .padding(3);

  // Compute the hierarchy from the (flat) data; expose the values
  // for each node; lastly apply the pack layout.
  const root = pack(d3.hierarchy({ children: data }).sum((d) => d.count));

  // Create the SVG container.
  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [-margin, -margin, width, height])
    .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;")
    .attr("text-anchor", "middle");

  // Place each (leaf) node according to the layout’s x and y values.
  const node = svg
    .append("g")
    .selectAll()
    .data(root.leaves())
    .join("g")
    .attr("transform", (d) => `translate(${d.x},${d.y})`);

  // Add a filled circle.
  node
    .append("circle")
    .attr("fill-opacity", 0.7)
    .attr("fill", (d) => color(d.data))
    .attr("r", (d) => d.r);

  // Add a label.
  const text = node.append("text").attr("clip-path", (d) => `circle(${d.r})`);

  // Add a tspan for each CamelCase-separated word.
  text
    .selectAll()
    .data((d) => [name(d.data)])
    .join("tspan")
    .attr("x", 0)
    .attr("y", (d, i, nodes) => `${i - nodes.length / 2 + 0.35}em`)
    .text((d) => d);

  // Add a tspan for the node’s value.
  text
    .append("tspan")
    .attr("x", 0)
    .attr("y", (d) => `${names(d.data).length / 2 + 0.35}em`)
    .attr("fill-opacity", 0.7)
    .text((d) => format(d.value));

  return svg.node();
}

export function EmbeddingsVisualization(props: EmbeddingsVisualizationProps) {
  const clipIndex = props.clipIndex;
  const clipsCollection = props.clipsCollection;
  const clip = clipsCollection.clips[clipIndex];

  const [humanFriendlyTokens, setHumanFriendlyTokens] = useState<boolean>(true);

  function displayToken(token: string) {
    if (humanFriendlyTokens) {
      return prettifyToken(token);
    } else {
      return codifyToken(token);
    }
  }

  const bubbleChartSvg = renderBubbleChart([
    ...countNeighbors(clip.embedding_neighbor_tokens_mae || [], "MAE"),
    ...countNeighbors(clip.embedding_neighbor_tokens_dino || [], "DINO"),
    ...countNeighbors(clip.embedding_neighbor_tokens_s2v || [], "S2V"),
  ]);

  return (
    <Box sx={{ paddingTop: 5 }}>
      <Typography
        level="h2"
        sx={{ marginBottom: 2 }}
        startDecorator={<BubbleChartIcon />}
        endDecorator={
          <Chip variant="soft" startDecorator={<TheatersIcon />}>
            Clip index {clipIndex} of {clipsCollection.clips.length}
          </Chip>
        }
      >
        Embeddings visualization
      </Typography>

      <Stack direction="row" spacing={1} sx={{ paddingBottom: 1 }}>
        <Chip size="lg" color="primary">
          MAE embeddings: {clip.embedding_neighbor_tokens_mae?.length}
        </Chip>
        <Chip size="lg" color="success">
          DINO embeddings: {clip.embedding_neighbor_tokens_dino?.length}
        </Chip>
        <Chip size="lg" color="danger">
          S2V embeddings: {clip.embedding_neighbor_tokens_s2v?.length}
        </Chip>
      </Stack>

      <Box
        sx={{ textAlign: "center", paddingBottom: 1 }}
        dangerouslySetInnerHTML={{ __html: bubbleChartSvg.outerHTML }}
      ></Box>

      <Checkbox
        label="Human friendly"
        size="sm"
        checked={humanFriendlyTokens}
        onChange={(e) => setHumanFriendlyTokens(e.target.checked)}
      />
      <Typography level="body-xs" color="primary" gutterBottom>
        <strong>MAE:</strong>{" "}
        {clip.embedding_neighbor_tokens_mae?.map(displayToken).join(" ")}
      </Typography>
      <Typography level="body-xs" color="success" gutterBottom>
        <strong>DINO:</strong>{" "}
        {clip.embedding_neighbor_tokens_dino?.map(displayToken).join(" ")}
      </Typography>
      <Typography level="body-xs" color="danger" sx={{ paddingBottom: 2 }}>
        <strong>S2V:</strong>{" "}
        {clip.embedding_neighbor_tokens_s2v?.map(displayToken).join(" ")}
      </Typography>
    </Box>
  );
}
