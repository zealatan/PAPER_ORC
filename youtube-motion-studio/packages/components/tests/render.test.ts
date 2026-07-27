import { describe, expect, it } from "vitest";
import { renderProjectToSvg, SvgFrameRenderer } from "@motion-studio/renderer-core";
import { ronaldReadProject } from "@motion-studio/core";
import { createDefaultRenderRegistry } from "../src";
import { makeElement, makeProject, makeScene } from "./helpers";

const registry = createDefaultRenderRegistry();

// An M2 fixture exercising every built-in component + a couple of animations.
const fixture = makeProject([
  makeScene(
    "scene-1",
    [
      makeElement("bg", "rectangle", {
        transform: { x: 0, y: 0, width: 1080, height: 1920, zIndex: 0 },
        style: { backgroundColor: "#0f1115" },
      }),
      makeElement("panel", "group", {
        transform: { x: 140, y: 500, width: 800, height: 600, zIndex: 1 },
        style: { backgroundColor: "#1e222b", borderRadius: 24 },
        children: [
          makeElement("dot", "circle", {
            transform: { x: 40, y: 40, width: 120, height: 120 },
            style: { backgroundColor: "#ffd000" },
          }),
        ],
      }),
      makeElement("title", "text", {
        transform: { x: 540, y: 1300, width: 900, height: 120, zIndex: 2 },
        props: {
          text: "Deterministic",
          fontSize: 64,
          textAlign: "center",
          color: "#ffffff",
        },
        animations: [
          {
            id: "a1",
            kind: "preset",
            target: "opacity",
            start: 0,
            duration: 0.5,
            presetId: "fade-in",
          },
        ],
      }),
      makeElement("logo", "image", {
        transform: { x: 460, y: 200, width: 160, height: 160, zIndex: 3 },
        props: { assetId: "missing-logo" },
      }),
    ],
    5,
  ),
]);

describe("visual regression (SVG snapshots)", () => {
  it.each([0, 0.25, 1])("renders a stable frame at t=%s", (t) => {
    expect(renderProjectToSvg(fixture, t, registry)).toMatchSnapshot();
  });

  it("is deterministic for a fixed timestamp", () => {
    expect(renderProjectToSvg(fixture, 0.25, registry)).toBe(
      renderProjectToSvg(fixture, 0.25, registry),
    );
  });
});

describe("frame renderer over the fixture", () => {
  it("produces an SVG frame with all component primitives", async () => {
    const renderer = new SvgFrameRenderer(registry);
    await renderer.initialize(fixture);
    const frame = await renderer.renderFrame(1);
    // circle (ellipse), text, rounded panel rect, and image placeholder are all present.
    expect(frame.payload).toContain("<ellipse");
    expect(frame.payload).toContain("<text");
    expect(frame.payload).toContain("Deterministic");
    await renderer.dispose();
  });
});

describe("real sample + unknown types", () => {
  it("renders the Ronald Read sample without crashing", () => {
    // profile-card and caption are now real components (M7); the sample renders for real.
    const svg = renderProjectToSvg(ronaldReadProject, 1, registry);
    expect(svg.startsWith("<svg")).toBe(true);
    expect(svg).toContain("<text");
  });

  it("renders a visible placeholder for a genuinely unknown type", () => {
    const project = makeProject([
      makeScene("s", [makeElement("x", "totally-unknown-widget", {})]),
    ]);
    const svg = renderProjectToSvg(project, 0, registry);
    expect(svg).toContain("?totally-unknown-widget");
  });
});
