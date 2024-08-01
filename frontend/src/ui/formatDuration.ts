function zpad(value: number, digits: number): string {
  let text = String(value);
  while (text.length < digits) {
    text = "0" + text;
  }
  return text;
}

export function formatDuration(seconds?: number): string {
  if (seconds === undefined) return "unknown";
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds - minutes * 60);
  return zpad(minutes, 2) + ":" + zpad(remainingSeconds, 2);
}
