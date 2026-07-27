import { describe, expect, it } from "vitest";
import {
  activeCue,
  formatSrtTime,
  parseSrt,
  parseSrtTime,
  serializeSrt,
  type SubtitleCue,
} from "../src";

const SRT = `1
00:00:00,000 --> 00:00:02,500
Hello world

2
00:00:02,500 --> 00:00:05,000
Second line
across two rows`;

describe("SRT time", () => {
  it("formats and parses timestamps", () => {
    expect(formatSrtTime(3661.25)).toBe("01:01:01,250");
    expect(parseSrtTime("01:01:01,250")).toBeCloseTo(3661.25, 3);
    expect(parseSrtTime("00:00:02.500")).toBeCloseTo(2.5, 3);
  });
});

describe("parseSrt / serializeSrt", () => {
  it("parses cues with timing and multi-line text", () => {
    const cues = parseSrt(SRT);
    expect(cues).toHaveLength(2);
    expect(cues[0]).toMatchObject({ start: 0, end: 2.5, text: "Hello world" });
    expect(cues[1]?.text).toBe("Second line\nacross two rows");
  });

  it("round-trips losslessly", () => {
    const cues = parseSrt(SRT);
    const reparsed = parseSrt(serializeSrt(cues));
    expect(reparsed).toEqual(cues);
  });
});

describe("activeCue", () => {
  const cues: SubtitleCue[] = [
    { start: 0, end: 2, text: "a" },
    { start: 2, end: 4, text: "b" },
  ];
  it("selects the cue whose window contains the time", () => {
    expect(activeCue(cues, 1)?.text).toBe("a");
    expect(activeCue(cues, 2)?.text).toBe("b");
    expect(activeCue(cues, 3.99)?.text).toBe("b");
  });
  it("returns null outside any cue", () => {
    expect(activeCue(cues, 5)).toBeNull();
    expect(activeCue(cues, -1)).toBeNull();
  });
});
