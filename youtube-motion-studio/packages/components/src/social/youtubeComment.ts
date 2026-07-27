/**
 * "youtube-comment" social component. Renders a single YouTube-style comment: a circular
 * avatar (asset image when resolvable, otherwise a neutral placeholder circle), the author
 * name, the comment body, and a like count. Coordinates are element-local: the content box
 * spans `[0, 0] → [width, height]` from the resolved transform.
 */
import {
  type DrawNode,
  type EllipseNode,
  type ImageNode,
  type TextNode,
  group,
} from "@motion-studio/renderer-core";
import { z } from "zod";
import { type ComponentDefinition, readProps } from "../types";

export interface YoutubeCommentProps {
  author: string;
  text: string;
  likes: number;
  avatarAssetId?: string;
}

const propsSchema = z.object({
  author: z.string().default("User"),
  text: z.string().default("Nice video!"),
  likes: z.number().default(0),
  avatarAssetId: z.string().optional(),
});

const defaultProps: YoutubeCommentProps = {
  author: "User",
  text: "Nice video!",
  likes: 0,
};

export const youtubeCommentComponent: ComponentDefinition<YoutubeCommentProps> = {
  type: "youtube-comment",
  displayName: "YouTube Comment",
  category: "social",
  propsSchema,
  defaultProps,
  defaultTransform: { width: 820, height: 220 },
  render(element, ctx): DrawNode | null {
    const p = readProps(youtubeCommentComponent, element);
    const W = element.transform.width;
    const r = 36;

    const avatarHref = p.avatarAssetId ? ctx.resolveAssetUrl(p.avatarAssetId) : null;
    const avatar: EllipseNode | ImageNode =
      avatarHref !== null
        ? {
            kind: "image",
            x: 20,
            y: 4,
            width: 2 * r,
            height: 2 * r,
            href: avatarHref,
            radius: r,
          }
        : {
            kind: "ellipse",
            cx: r + 20,
            cy: 40,
            rx: r,
            ry: r,
            fill: { color: "#888888" },
          };

    const author: TextNode = {
      kind: "text",
      x: r + 70,
      y: 36,
      text: p.author,
      fontSize: 26,
      fontWeight: 700,
      fill: { color: "#ffffff" },
      align: "left",
      baseline: "middle",
    };

    const comment: TextNode = {
      kind: "text",
      x: r + 70,
      y: 96,
      text: p.text,
      fontSize: 28,
      fill: { color: "#e6e9ef" },
      align: "left",
      baseline: "middle",
      maxWidth: W - (r + 90),
    };

    const likeText: TextNode = {
      kind: "text",
      x: r + 70,
      y: 160,
      text: "👍 " + String(p.likes),
      fontSize: 22,
      fill: { color: "#9aa3b2" },
      align: "left",
      baseline: "middle",
    };

    return group([avatar, author, comment, likeText]);
  },
};
