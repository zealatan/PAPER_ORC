/**
 * Subtitle component (spec §16.3). A subtitle is an ordinary element whose props carry cue data;
 * at render time it shows the cue active at the frame's scene-local time (`ctx.sceneTime`). This is
 * the one component that is time-aware — cue selection is deterministic for a given timestamp.
 */
import { z } from "zod";
import { activeCue, type SubtitleCue } from "@motion-studio/core";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import { type ComponentDefinition, readProps } from "../types";

interface SubtitleProps {
  cues: SubtitleCue[];
  fontSize: number;
  color: string;
  background: string;
}

const propsSchema = z.object({
  cues: z
    .array(z.object({ start: z.number(), end: z.number(), text: z.string() }))
    .default([]),
  fontSize: z.number().default(44),
  color: z.string().default("#ffffff"),
  background: z.string().default("#000000b3"),
});

const defaultProps: SubtitleProps = {
  cues: [],
  fontSize: 44,
  color: "#ffffff",
  background: "#000000b3",
};

export const subtitleComponent: ComponentDefinition<SubtitleProps> = {
  type: "subtitle",
  displayName: "Subtitle",
  category: "text",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 900, height: 120 },
  render(element, ctx) {
    const p = readProps(subtitleComponent, element);
    const cue = activeCue(p.cues, ctx.sceneTime);
    if (!cue || cue.text.length === 0) return null;

    const w = element.transform.width;
    const h = element.transform.height;
    const nodes: DrawNode[] = [];
    if (p.background) {
      nodes.push({
        kind: "rect",
        x: 0,
        y: 0,
        width: w,
        height: h,
        radius: 10,
        fill: { color: p.background },
      });
    }
    nodes.push({
      kind: "text",
      x: w / 2,
      y: h / 2,
      text: cue.text,
      fontSize: p.fontSize,
      fontWeight: 700,
      fill: { color: p.color },
      align: "center",
      baseline: "middle",
      maxWidth: w - 40,
    });
    return group(nodes);
  },
};
