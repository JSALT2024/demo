export interface Clip {
  readonly start_frame: number;
  readonly frame_count: number;
  readonly translation_context: string | null;
  readonly translation_result: string | null;
  readonly embedding_neighbor_tokens_mae: string[] | null;
  readonly embedding_neighbor_tokens_dino: string[] | null;
  readonly embedding_neighbor_tokens_s2v: string[] | null;
}
