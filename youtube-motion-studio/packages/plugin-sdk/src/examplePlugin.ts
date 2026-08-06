/**
 * Example plugin (spec §19). Demonstrates a trusted local plugin that registers a "sticker"
 * component and a theme through the permission-gated API. Used by the plugin host tests.
 */
import { z } from "zod";
import { type DrawNode, group } from "@motion-studio/renderer-core";
import type { ComponentDefinition } from "@motion-studio/components";
import type { Theme } from "@motion-studio/core";
import type { PluginManifest } from "./manifest";
import type { LoadablePlugin, MotionStudioPlugin } from "./host";

interface StickerProps {
  label: string;
  color: string;
}

const stickerSchema = z.object({
  label: z.string().default("★"),
  color: z.string().default("#ff3b30"),
});

const stickerComponent: ComponentDefinition<StickerProps> = {
  type: "sticker",
  displayName: "Sticker",
  category: "shape",
  propsSchema: stickerSchema,
  defaultProps: { label: "★", color: "#ff3b30" },
  defaultTransform: { width: 200, height: 200 },
  render(element): DrawNode {
    const parsed = stickerSchema.safeParse(element.props);
    const props = parsed.success ? parsed.data : { label: "★", color: "#ff3b30" };
    const w = element.transform.width;
    const h = element.transform.height;
    return group([
      {
        kind: "ellipse",
        cx: w / 2,
        cy: h / 2,
        rx: w / 2,
        ry: h / 2,
        fill: { color: props.color },
      },
      {
        kind: "text",
        x: w / 2,
        y: h / 2,
        text: props.label,
        fontSize: Math.min(w, h) * 0.5,
        fill: { color: "#ffffff" },
        align: "center",
        baseline: "middle",
      },
    ]);
  },
};

const stickerTheme: Theme = {
  id: "sticker-pop",
  name: "Sticker Pop",
  tokens: {
    colors: {
      background: "#1a0033",
      surface: "#2b0a4d",
      text: "#ffffff",
      textSecondary: "#c9a3ff",
      accent: "#ff3b30",
    },
  },
};

export const exampleManifest: PluginManifest = {
  id: "example-stickers",
  name: "Example Stickers",
  version: "1.0.0",
  engine: { minimumVersion: "0.1.0" },
  permissions: ["register-components", "register-themes"],
};

export const examplePlugin: MotionStudioPlugin = {
  activate(api) {
    api.registerComponent(stickerComponent);
    api.registerTheme(stickerTheme);
    api.log("Stickers activated");
  },
};

export const exampleLoadable: LoadablePlugin = {
  manifest: exampleManifest,
  plugin: examplePlugin,
};
