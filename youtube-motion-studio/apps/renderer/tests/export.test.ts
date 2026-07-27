import { spawnSync } from "node:child_process";
import { existsSync, rmSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterAll, describe, expect, it } from "vitest";
import {
  DEFAULT_TRANSFORM,
  createEmptyProject,
  type MotionElement,
  type MotionProject,
} from "@motion-studio/core";
import { buildFfmpegArgs, exportVideo, ffmpegAvailable } from "../src";

const HAS_FFMPEG = await ffmpegAvailable();
const OUT = join(tmpdir(), "motion-studio-export-test.mp4");

function rect(id: string): MotionElement {
  return {
    id,
    type: "rectangle",
    name: id,
    visible: true,
    locked: false,
    transform: {
      ...DEFAULT_TRANSFORM,
      x: 0,
      y: 0,
      width: 1080,
      height: 1920,
      anchorX: 0,
      anchorY: 0,
    },
    style: { backgroundColor: "#ffd000" },
    props: {},
    timing: { start: 0, duration: 1 },
    animations: [],
  };
}

function tinyProject(): MotionProject {
  const project = createEmptyProject({
    id: "export-test",
    name: "Export Test",
    now: "2026-01-01T00:00:00.000Z",
  });
  return {
    ...project,
    settings: { ...project.settings, fps: 12 },
    scenes: [
      {
        id: "s1",
        name: "S1",
        duration: 0.5,
        background: { type: "solid", color: "#101015" },
        elements: [rect("bg")],
      },
    ],
  };
}

function ffprobe(path: string): {
  width: number;
  height: number;
  codec: string;
  duration: number;
} {
  const out = spawnSync(
    "ffprobe",
    [
      "-v",
      "error",
      "-select_streams",
      "v:0",
      "-show_entries",
      "stream=width,height,codec_name",
      "-show_entries",
      "format=duration",
      "-of",
      "json",
      path,
    ],
    { encoding: "utf8" },
  );
  const json = JSON.parse(out.stdout) as {
    streams: Array<{ width: number; height: number; codec_name: string }>;
    format: { duration: string };
  };
  const stream = json.streams[0]!;
  return {
    width: stream.width,
    height: stream.height,
    codec: stream.codec_name,
    duration: Number(json.format.duration),
  };
}

describe("buildFfmpegArgs", () => {
  it("targets H.264 / yuv420p / faststart", () => {
    const args = buildFfmpegArgs({
      fps: 30,
      crf: 20,
      preset: "medium",
      outPath: "/tmp/x.mp4",
      ffmpegPath: "ffmpeg",
    });
    expect(args).toContain("libx264");
    expect(args).toContain("yuv420p");
    expect(args.join(" ")).toContain("+faststart");
    expect(args.join(" ")).toContain("-framerate 30");
  });
});

describe("exportVideo (integration)", () => {
  afterAll(() => {
    try {
      rmSync(OUT, { force: true });
    } catch {
      /* ignore */
    }
  });

  it.skipIf(!HAS_FFMPEG)(
    "exports a valid 1080x1920 H.264 MP4 matching the project",
    async () => {
      const project = tinyProject();
      const progress: number[] = [];
      const result = await exportVideo(project, { outPath: OUT }, (p) =>
        progress.push(p.frame),
      );

      expect(existsSync(OUT)).toBe(true);
      expect(statSync(OUT).size).toBeGreaterThan(0);
      expect(result.report.frameCount).toBe(6); // 0.5s * 12fps
      expect(progress.at(-1)).toBe(6);

      const info = ffprobe(OUT);
      expect(info.width).toBe(1080);
      expect(info.height).toBe(1920);
      expect(info.codec).toBe("h264");
      expect(info.duration).toBeGreaterThan(0.3);
      expect(info.duration).toBeLessThan(0.8);
    },
  );

  it.skipIf(!HAS_FFMPEG)("cancels and removes the partial file", async () => {
    const controller = new AbortController();
    controller.abort();
    await expect(
      exportVideo(tinyProject(), { outPath: OUT }, undefined, controller.signal),
    ).rejects.toThrow(/cancel/i);
  });

  it.skipIf(!HAS_FFMPEG)("composites a video background into the export", async () => {
    const bgPath = join(tmpdir(), "motion-studio-test-bg.mp4");
    const out = join(tmpdir(), "motion-studio-export-bg.mp4");
    spawnSync("ffmpeg", [
      "-y",
      "-f",
      "lavfi",
      "-i",
      "color=c=red:s=320x240:d=1:r=12",
      "-pix_fmt",
      "yuv420p",
      bgPath,
    ]);
    const project: MotionProject = {
      ...tinyProject(),
      settings: { ...tinyProject().settings, width: 320, height: 240, fps: 12 },
      assets: [
        {
          id: "bg",
          type: "video",
          name: "bg",
          source: { kind: "local-path", path: bgPath },
        },
      ],
      scenes: [
        {
          id: "s1",
          name: "S1",
          duration: 0.5,
          background: { type: "video", assetId: "bg", fit: "cover" },
          elements: [rect("fg")],
        },
      ],
    };
    const result = await exportVideo(project, { outPath: out });
    expect(result.report.ffmpegCommand).toContain("overlay");
    expect(existsSync(out)).toBe(true);
    expect(ffprobe(out).codec).toBe("h264");
    rmSync(bgPath, { force: true });
    rmSync(out, { force: true });
  });
});
