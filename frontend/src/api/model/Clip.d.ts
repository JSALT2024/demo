export interface Clip {
  readonly start_frame: number;
  readonly frame_count: number;
  readonly translation_context: string | null;
  readonly translation_result: string | null;
}
