/**
 * "image" media component. Renders a resolved asset (by id or direct src) as an
 * {@link ImageNode}, falling back to a neutral placeholder rect when no source resolves
 * (spec §8.2: components stay usable on unknown/invalid props).
 */
import type { MotionElement } from "@motion-studio/core";
import type {
  DrawNode,
  ImageNode,
  RectNode,
  RenderContext,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

const imagePropsSchema = z.object({
  assetId: z.string().optional(),
  src: z.string().optional(),
  fit: z.enum(["cover", "contain", "fill", "none"]).optional(),
  radius: z.number().optional(),
});

export type ImageProps = z.infer<typeof imagePropsSchema>;

export const imageComponent: ComponentDefinition<ImageProps> = {
  type: "image",
  displayName: "Image",
  category: "media",
  icon: "image",
  propsSchema: imagePropsSchema,
  defaultProps: {},
  defaultTransform: { width: 480, height: 480 },
  render(element: MotionElement, ctx: RenderContext): DrawNode | null {
    const p = readProps(imageComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const href = (p.assetId ? ctx.resolveAssetUrl(p.assetId) : null) ?? p.src ?? null;

    if (href === null) {
      const placeholder: RectNode = {
        kind: "rect",
        x: 0,
        y: 0,
        width: W,
        height: H,
        fill: { color: "#2a2f3a" },
        stroke: { color: "#3a3f4a", width: 2 },
      };
      return placeholder;
    }

    const image: ImageNode = {
      kind: "image",
      x: 0,
      y: 0,
      width: W,
      height: H,
      href,
      fit: p.fit,
      radius: p.radius,
    };
    return image;
  },
};
