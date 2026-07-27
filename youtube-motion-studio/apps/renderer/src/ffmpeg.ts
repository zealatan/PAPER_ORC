/**
 * FFmpeg encoding: PNG frames piped over stdin → H.264 MP4 (yuv420p, faststart). Arguments are
 * built as an array and never shell-interpolated (spec §35: escape FFmpeg arguments).
 */
import { spawn, type ChildProcessByStdio } from "node:child_process";
import type { Readable, Writable } from "node:stream";

type FfmpegChild = ChildProcessByStdio<Writable, null, Readable>;

export interface FfmpegConfig {
  fps: number;
  crf: number;
  preset: string;
  outPath: string;
  ffmpegPath: string;
}

export function buildFfmpegArgs(config: FfmpegConfig): string[] {
  return [
    "-y",
    "-f",
    "image2pipe",
    "-framerate",
    String(config.fps),
    "-i",
    "-",
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-crf",
    String(config.crf),
    "-preset",
    config.preset,
    "-movflags",
    "+faststart",
    "-r",
    String(config.fps),
    config.outPath,
  ];
}

export interface FfmpegProcess {
  child: FfmpegChild;
  command: string;
  /** Resolves when ffmpeg exits 0; rejects with stderr tail otherwise. */
  done: Promise<void>;
}

export function spawnFfmpeg(config: FfmpegConfig): FfmpegProcess {
  const args = buildFfmpegArgs(config);
  const child: FfmpegChild = spawn(config.ffmpegPath, args, {
    stdio: ["pipe", "ignore", "pipe"],
  });

  let stderr = "";
  child.stderr.on("data", (chunk: Buffer) => {
    stderr += chunk.toString();
    if (stderr.length > 8000) stderr = stderr.slice(-8000);
  });

  const done = new Promise<void>((resolve, reject) => {
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) resolve();
      else reject(new Error(`ffmpeg exited with code ${code}:\n${stderr.slice(-1000)}`));
    });
  });

  return { child, command: [config.ffmpegPath, ...args].join(" "), done };
}

/** Whether an ffmpeg executable is runnable. */
export function ffmpegAvailable(ffmpegPath = "ffmpeg"): Promise<boolean> {
  return new Promise((resolve) => {
    try {
      const child = spawn(ffmpegPath, ["-version"], { stdio: "ignore" });
      child.on("error", () => resolve(false));
      child.on("close", (code) => resolve(code === 0));
    } catch {
      resolve(false);
    }
  });
}
