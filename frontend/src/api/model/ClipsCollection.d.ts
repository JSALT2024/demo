import { Clip } from "./Clip";

export interface ClipsCollection {
  readonly clips: Clip[];
  readonly clip_index_lookup: number[];
}
