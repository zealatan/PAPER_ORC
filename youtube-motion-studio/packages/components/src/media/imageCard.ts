/**
 * "image-card" component (spec §8.1). Renders an image (resolved from an asset id or a raw src)
 * into a rounded card, with an optional caption bar along the bottom. Coordinates are
 * element-local: the content box spans `[0, 0] → [width, height]` from the resolved transform.
 */
import type { MotionElement } from "@motion-studio/core";
import {
  type DrawNode,
  type ImageNode,
  type RectNode,
  type RenderContext,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface ImageCardProps {
  assetId?: string;
  src?: string;
  caption?: string;
  radius: number;
}

const propsSchema = z.object({
  assetId: z.string().optional(),
  src: z.string().optional(),
  caption: z.string().optional(),
  radius: z.number().default(20),
});

const defaultProps: ImageCardProps = {
  radius: 20,
};

export const imageCardComponent: ComponentDefinition<ImageCardProps> = {
  type: "image-card",
  displayName: "Image Card",
  category: "media",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 520, height: 560 },
  render(element: MotionElement, ctx: RenderContext): DrawNode | null {
    const p = readProps(imageCardComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const href = (p.assetId ? ctx.resolveAssetUrl(p.assetId) : null) ?? p.src ?? null;
    const capH = p.caption ? 72 : 0;
    const imageH = H - capH;

    const children: DrawNode[] = [];

    if (href) {
      const imageNode: ImageNode = {
        kind: "image",
        x: 0,
        y: 0,
        width: W,
        height: imageH,
        href,
        radius: p.radius,
        fit: "cover",
      };
      children.push(imageNode);
    } else {
      const placeholder: RectNode = {
        kind: "rect",
        x: 0,
        y: 0,
        width: W,
        height: imageH,
        fill: { color: "#2a2f3a" },
        stroke: { color: "#3a3f4a", width: 2 },
        radius: p.radius,
      };
      children.push(placeholder);
    }

    if (p.caption) {
      const captionBg: RectNode = {
        kind: "rect",
        x: 0,
        y: H - capH,
        width: W,
        height: capH,
        fill: { color: "#111111" },
      };
      const captionText: TextNode = {
        kind: "text",
        x: W / 2,
        y: H - capH / 2,
        text: p.caption,
        fontSize: 30,
        fill: { color: "#ffffff" },
        align: "center",
        baseline: "middle",
      };
      children.push(captionBg, captionText);
    }

    return group(children);
  },
};
