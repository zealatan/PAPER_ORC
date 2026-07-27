import { describe, expect, it } from "vitest";
import { findElementById, validateProject } from "@motion-studio/core";
import { pgDeckAdapter } from "../src";

const deck = {
  theme: "blueprint",
  paper: "photo",
  scenes: [
    {
      tpl: "hero",
      sid: 1,
      dur: 5000,
      bgid: "pg_storefront",
      data: { eye: "배당왕", big: "70년", under: "연속 배당 증액" },
      subLines: ["첫 번째 줄입니다.", "두 번째 줄입니다."],
    },
    {
      tpl: "enginechart",
      sid: 2,
      dur: 10000,
      data: { title: "복리의 힘", sub: "26년 백테스트" },
      subLines: [],
    },
  ],
};
const input = JSON.stringify(deck);

describe("pgDeckAdapter.detect", () => {
  it("recognizes a PG deck JSON", () => {
    const result = pgDeckAdapter.detect(input);
    expect(result.isLegacy).toBe(true);
    expect(result.kind).toBe("pg-deck");
  });

  it("rejects non-deck input", () => {
    expect(pgDeckAdapter.detect("not json").isLegacy).toBe(false);
    expect(pgDeckAdapter.detect(JSON.stringify({ hello: 1 })).isLegacy).toBe(false);
  });
});

describe("pgDeckAdapter.import", () => {
  it("produces a valid MotionProject with translated text", async () => {
    const { project } = await pgDeckAdapter.import(input);
    expect(() => validateProject(project)).not.toThrow();
    expect(project.scenes).toHaveLength(2);
    expect(project.settings.width).toBe(1920);
    expect(project.settings.height).toBe(1080);

    // Hero scene text was translated into elements.
    expect(findElementById(project, "scene-1-title")?.element.props.text).toBe("70년");
    expect(findElementById(project, "scene-1-eyebrow")?.element.props.text).toBe(
      "배당왕",
    );
  });

  it("distributes subLines into subtitle cues", async () => {
    const { project } = await pgDeckAdapter.import(input);
    const subs = findElementById(project, "scene-1-subtitle")?.element;
    expect(subs?.type).toBe("subtitle");
    const cues = subs?.props.cues as Array<{ start: number; end: number; text: string }>;
    expect(cues).toHaveLength(2);
    expect(cues[0]).toMatchObject({ start: 0, end: 2.5, text: "첫 번째 줄입니다." });
    expect(cues[1]?.start).toBe(2.5);
  });

  it("imports chart templates as placeholders and reports them", async () => {
    const { project, report } = await pgDeckAdapter.import(input);
    expect(findElementById(project, "scene-2-placeholder")?.element.type).toBe(
      "rectangle",
    );
    expect(report.unsupported).toHaveLength(1);
    expect(report.unsupported[0]?.reason).toMatch(/enginechart/);
    // background video became an asset request.
    expect(report.assetRequests.map((a) => a.id)).toContain("pg_storefront");
    expect(report.importedScenes).toBe(2);
  });
});
