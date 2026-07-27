/**
 * A small demo project built entirely from the built-in M2 components. It exists so the editor
 * shell can render a real frame through the deterministic renderer — proving the engine works in
 * the browser, not just in tests. It hardcodes no engine behaviour; it is ordinary project data.
 */
import {
  DEFAULT_TRANSFORM,
  createEmptyProject,
  type MotionElement,
  type MotionProject,
  type Transform2D,
} from "@motion-studio/core";

function t(overrides: Partial<Transform2D>): Transform2D {
  return { ...DEFAULT_TRANSFORM, anchorX: 0, anchorY: 0, ...overrides };
}

function el(
  id: string,
  type: string,
  transform: Partial<Transform2D>,
  extra: Partial<MotionElement> = {},
): MotionElement {
  return {
    id,
    type,
    name: id,
    visible: true,
    locked: false,
    transform: t(transform),
    style: extra.style ?? {},
    props: extra.props ?? {},
    timing: extra.timing ?? { start: 0, duration: 5 },
    animations: extra.animations ?? [],
    ...(extra.children ? { children: extra.children } : {}),
  };
}

export const demoProject: MotionProject = {
  ...createEmptyProject({
    id: "demo",
    name: "M2 Renderer Demo",
    now: "2026-07-27T00:00:00.000Z",
  }),
  scenes: [
    {
      id: "scene-1",
      name: "Demo",
      duration: 5,
      background: {
        type: "gradient",
        angle: 90,
        stops: [
          { color: "#12203a", position: 0 },
          { color: "#0b1120", position: 1 },
        ],
      },
      elements: [
        el(
          "card",
          "group",
          { x: 140, y: 560, width: 800, height: 760, zIndex: 1 },
          {
            style: { backgroundColor: "#1e222b", borderRadius: 28 },
            children: [
              el(
                "dot",
                "circle",
                { x: 320, y: 80, width: 160, height: 160 },
                {
                  style: { backgroundColor: "#ffd000" },
                  animations: [
                    {
                      id: "pop",
                      kind: "preset",
                      target: "transform",
                      start: 0,
                      duration: 0.6,
                      presetId: "pop-in",
                      params: { overshoot: 1.15 },
                    },
                  ],
                },
              ),
            ],
          },
        ),
        el(
          "title",
          "text",
          { x: 540, y: 1360, width: 900, height: 120, zIndex: 2 },
          {
            props: {
              text: "Deterministic Render",
              fontSize: 68,
              fontWeight: 800,
              textAlign: "center",
              color: "#ffffff",
            },
            animations: [
              {
                id: "fade",
                kind: "preset",
                target: "opacity",
                start: 0.3,
                duration: 0.5,
                presetId: "fade-in",
              },
            ],
          },
        ),
        el(
          "tag",
          "text",
          { x: 540, y: 1520, width: 900, height: 80, zIndex: 2 },
          {
            props: {
              text: "1080 × 1920 · SVG backend",
              fontSize: 34,
              textAlign: "center",
              color: "#9aa3b2",
            },
          },
        ),
      ],
    },
  ],
};
