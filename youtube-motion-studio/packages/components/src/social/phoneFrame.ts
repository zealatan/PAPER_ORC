/**
 * "phone-frame" component (spec §8.1). Renders a stylized phone chrome: a rounded body, an inset
 * screen (image asset or solid fill), and a top notch. Coordinates are element-local: the content
 * box spans `[0, 0] → [width, height]` from the resolved transform.
 */
import {
  type DrawNode,
  type ImageNode,
  type RectNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface PhoneFrameProps {
  bodyColor: string;
  screenColor: string;
  assetId?: string;
}

const propsSchema = z.object({
  bodyColor: z.string().default("#0b0e14"),
  screenColor: z.string().default("#000000"),
  assetId: z.string().optional(),
});

const defaultProps: PhoneFrameProps = {
  bodyColor: "#0b0e14",
  screenColor: "#000000",
};

export const phoneFrameComponent: ComponentDefinition<PhoneFrameProps> = {
  type: "phone-frame",
  displayName: "Phone Frame",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 360, height: 740 },
  render(element, ctx): DrawNode | null {
    const p = readProps(phoneFrameComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;
    const m = W * 0.05;

    const screenX = m;
    const screenY = m * 1.4;
    const screenW = W - 2 * m;
    const screenH = H - 2 * m * 1.4;
    const screenRadius = W * 0.08;

    const body: RectNode = {
      kind: "rect",
      x: 0,
      y: 0,
      width: W,
      height: H,
      radius: W * 0.12,
      fill: { color: p.bodyColor },
    };

    const href = p.assetId ? ctx.resolveAssetUrl(p.assetId) : null;
    const screen: DrawNode = href
      ? ({
          kind: "image",
          x: screenX,
          y: screenY,
          width: screenW,
          height: screenH,
          href,
          radius: screenRadius,
          fit: "cover",
        } satisfies ImageNode)
      : ({
          kind: "rect",
          x: screenX,
          y: screenY,
          width: screenW,
          height: screenH,
          radius: screenRadius,
          fill: { color: p.screenColor },
        } satisfies RectNode);

    const notch: RectNode = {
      kind: "rect",
      x: W * 0.36,
      y: m * 0.5,
      width: W * 0.28,
      height: 14,
      radius: 7,
      fill: { color: "#000000" },
    };

    return group([body, screen, notch]);
  },
};
