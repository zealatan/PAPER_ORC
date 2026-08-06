import { describe, expect, it } from "vitest";
import { DefaultRenderRegistry } from "../src/registry";
import { renderProjectToSvg, SvgFrameRenderer } from "../src/renderers/svg";
import type { ElementRenderer } from "../src/types";
import { makeElement, makeProject, makeScene } from "./helpers";

const boxRenderer: ElementRenderer = {
  type: "box",
  render: (element) => ({
    kind: "rect",
    x: 0,
    y: 0,
    width: element.transform.width,
    height: element.transform.height,
    fill: { color: "#ff0000" },
  }),
};

function registry(): DefaultRenderRegistry {
  const r = new DefaultRenderRegistry();
  r.register(boxRenderer);
  return r;
}

const project = makeProject([
  makeScene("s1", [
    makeElement("known", "box", { transform: { x: 10, y: 20, width: 100, height: 50 } }),
    makeElement("unknown", "mystery-widget", { transform: { width: 80, height: 80 } }),
  ]),
]);

describe("renderProjectToSvg", () => {
  it("emits an SVG sized to the composition", () => {
    const svg = renderProjectToSvg(project, 0, registry());
    expect(svg.startsWith("<svg")).toBe(true);
    expect(svg).toContain('width="1080"');
    expect(svg).toContain('height="1920"');
    expect(svg).toContain('viewBox="0 0 1080 1920"');
  });

  it("paints the composition and scene backgrounds", () => {
    const svg = renderProjectToSvg(project, 0, registry());
    expect(svg).toContain('fill="#000000"'); // composition background
    expect(svg).toContain('fill="#101010"'); // scene solid background
  });

  it("renders a known component's primitives", () => {
    const svg = renderProjectToSvg(project, 0, registry());
    expect(svg).toContain('fill="#ff0000"');
    expect(svg).toContain("matrix(1 0 0 1 10 20)");
  });

  it("renders a visible placeholder for an unknown type", () => {
    const svg = renderProjectToSvg(project, 0, registry());
    expect(svg).toContain("?mystery-widget");
    expect(svg).toContain("#ff00ff");
  });

  it("is deterministic (same time → identical bytes)", () => {
    expect(renderProjectToSvg(project, 0, registry())).toBe(
      renderProjectToSvg(project, 0, registry()),
    );
  });

  it("can prepend an XML declaration", () => {
    const svg = renderProjectToSvg(project, 0, registry(), {
      includeXmlDeclaration: true,
    });
    expect(svg.startsWith("<?xml")).toBe(true);
  });
});

describe("SvgFrameRenderer", () => {
  it("implements the FrameRenderer contract", async () => {
    const renderer = new SvgFrameRenderer(registry());
    await renderer.initialize(project);
    const frame = await renderer.renderFrame(0);
    expect(frame.width).toBe(1080);
    expect(frame.height).toBe(1920);
    expect(frame.mediaType).toBe("image/svg+xml");
    expect(frame.payload).toContain("<svg");
    await renderer.dispose();
  });

  it("rejects renderFrame before initialize", async () => {
    const renderer = new SvgFrameRenderer(registry());
    await expect(renderer.renderFrame(0)).rejects.toThrow();
  });
});
