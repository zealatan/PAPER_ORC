/**
 * Subtitles (spec §16.3). Subtitles are plain data (an array of {@link SubtitleCue}) carried by an
 * ordinary "subtitle" element's props; the renderer shows the active cue for the current time.
 * SRT import/export is a lossless round-trip on cue timing and text.
 */
export interface SubtitleCue {
  /** Start time in seconds (scene-local). */
  start: number;
  /** End time in seconds (scene-local). */
  end: number;
  text: string;
}

function pad(n: number, width = 2): string {
  return String(Math.floor(n)).padStart(width, "0");
}

/** Format seconds as an SRT timestamp `HH:MM:SS,mmm`. */
export function formatSrtTime(seconds: number): string {
  const clamped = Math.max(0, seconds);
  const ms = Math.round((clamped - Math.floor(clamped)) * 1000);
  const total = Math.floor(clamped);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  return `${pad(h)}:${pad(m)}:${pad(s)},${pad(ms, 3)}`;
}

/** Parse an SRT timestamp `HH:MM:SS,mmm` (or with `.`) to seconds. */
export function parseSrtTime(value: string): number {
  const match = value.trim().match(/(\d+):(\d{2}):(\d{2})[,.](\d{1,3})/);
  if (!match) return 0;
  const [, h, m, s, ms] = match;
  return Number(h) * 3600 + Number(m) * 60 + Number(s) + Number(ms.padEnd(3, "0")) / 1000;
}

/** Parse SRT text into cues. Tolerant of blank lines and CRLF. */
export function parseSrt(input: string): SubtitleCue[] {
  const cues: SubtitleCue[] = [];
  const blocks = input
    .replace(/\r\n/g, "\n")
    .trim()
    .split(/\n{2,}/);
  for (const block of blocks) {
    const lines = block.split("\n");
    const timeLineIndex = lines.findIndex((l) => l.includes("-->"));
    if (timeLineIndex === -1) continue;
    const [startRaw, endRaw] = lines[timeLineIndex]!.split("-->");
    if (startRaw === undefined || endRaw === undefined) continue;
    const text = lines
      .slice(timeLineIndex + 1)
      .join("\n")
      .trim();
    cues.push({ start: parseSrtTime(startRaw), end: parseSrtTime(endRaw), text });
  }
  return cues;
}

/** Serialize cues to SRT text. */
export function serializeSrt(cues: SubtitleCue[]): string {
  return cues
    .map((cue, i) => {
      const time = `${formatSrtTime(cue.start)} --> ${formatSrtTime(cue.end)}`;
      return `${i + 1}\n${time}\n${cue.text}`;
    })
    .join("\n\n");
}

/** The cue active at a given time (last one whose window contains `time`), or null. */
export function activeCue(cues: SubtitleCue[], time: number): SubtitleCue | null {
  let active: SubtitleCue | null = null;
  for (const cue of cues) {
    if (time >= cue.start && time < cue.end) active = cue;
  }
  return active;
}
