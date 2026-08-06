/**
 * "profile-card" social component. Renders a rounded card with an avatar (resolved asset
 * image, or an accent-colored circle placeholder) beside a title and optional subtitle.
 * Coordinates are element-local: the content box spans `[0, 0] → [width, height]`.
 */
import {
  type DrawNode,
  type EllipseNode,
  type ImageNode,
  type RectNode,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

const propsSchema = z.object({
  title: z.string().default("Name"),
  subtitle: z.string().default(""),
  avatarAssetId: z.string().optional(),
  accent: z.string().default("#ffd000"),
  background: z.string().default("#1e222b"),
  color: z.string().default("#ffffff"),
});

export type ProfileCardProps = z.infer<typeof propsSchema>;

const defaultProps: ProfileCardProps = {
  title: "Name",
  subtitle: "",
  accent: "#ffd000",
  background: "#1e222b",
  color: "#ffffff",
};

export const profileCardComponent: ComponentDefinition<ProfileCardProps> = {
  type: "profile-card",
  displayName: "Profile Card",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 820, height: 260 },
  render(element, ctx): DrawNode | null {
    const p = readProps(profileCardComponent, element);
    const W = element.transform.width;
    const H = element.transform.height;

    const bg: RectNode = {
      kind: "rect",
      x: 0,
      y: 0,
      width: W,
      height: H,
      radius: 24,
      fill: { color: p.background },
    };

    const r = H * 0.32;
    const cx = r + 40;
    const cy = H / 2;

    const href = p.avatarAssetId ? ctx.resolveAssetUrl(p.avatarAssetId) : null;
    const avatar: ImageNode | EllipseNode = href
      ? {
          kind: "image",
          x: cx - r,
          y: cy - r,
          width: 2 * r,
          height: 2 * r,
          href,
          radius: r,
          fit: "cover",
        }
      : {
          kind: "ellipse",
          cx,
          cy,
          rx: r,
          ry: r,
          fill: { color: p.accent },
        };

    const textX = cx + r + 30;

    const title: TextNode = {
      kind: "text",
      x: textX,
      y: H / 2 - 22,
      text: p.title,
      fontSize: 44,
      fontWeight: 800,
      fill: { color: p.color },
      align: "left",
      baseline: "middle",
    };

    const nodes: DrawNode[] = [bg, avatar, title];

    if (p.subtitle) {
      const subtitle: TextNode = {
        kind: "text",
        x: textX,
        y: H / 2 + 30,
        text: p.subtitle,
        fontSize: 28,
        fill: { color: "#9aa3b2" },
        align: "left",
        baseline: "middle",
      };
      nodes.push(subtitle);
    }

    return group(nodes);
  },
};
