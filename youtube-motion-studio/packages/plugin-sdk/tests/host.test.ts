import { describe, expect, it } from "vitest";
import { z } from "zod";
import {
  PluginActivationError,
  type MotionTemplate,
  type Theme,
} from "@motion-studio/core";
import { DefaultComponentRegistry } from "@motion-studio/components";
import {
  ENGINE_VERSION,
  PluginHost,
  exampleLoadable,
  type LoadablePlugin,
  type PluginHostTargets,
} from "../src";

function makeHost(): { host: PluginHost; targets: PluginHostTargets } {
  const themes: Theme[] = [];
  const templates: MotionTemplate[] = [];
  const targets: PluginHostTargets = {
    engineVersion: ENGINE_VERSION,
    components: new DefaultComponentRegistry(),
    themes,
    templates,
  };
  return { host: new PluginHost(targets), targets };
}

describe("PluginHost", () => {
  it("registers and then removes a plugin's component (reversible)", async () => {
    const { host, targets } = makeHost();
    await host.load(exampleLoadable);
    expect(targets.components.has("sticker")).toBe(true);
    expect(targets.themes.some((t) => t.id === "sticker-pop")).toBe(true);
    expect(host.listLoaded()).toContain("example-stickers");

    await host.unload("example-stickers");
    expect(targets.components.has("sticker")).toBe(false);
    expect(targets.themes.some((t) => t.id === "sticker-pop")).toBe(false);
    expect(host.isLoaded("example-stickers")).toBe(false);
  });

  it("rejects a plugin that requires a newer engine", async () => {
    const { host } = makeHost();
    const incompatible: LoadablePlugin = {
      manifest: {
        id: "future",
        name: "Future",
        version: "1.0.0",
        engine: { minimumVersion: "99.0.0" },
        permissions: ["register-components"],
      },
      plugin: { activate: () => undefined },
    };
    await expect(host.load(incompatible)).rejects.toBeInstanceOf(PluginActivationError);
  });

  it("isolates an activation error and rolls back partial registrations", async () => {
    const { host, targets } = makeHost();
    const faulty: LoadablePlugin = {
      manifest: {
        id: "faulty",
        name: "Faulty",
        version: "1.0.0",
        engine: { minimumVersion: "0.1.0" },
        permissions: ["register-themes"],
      },
      plugin: {
        activate(api) {
          api.registerTheme({
            id: "temp",
            name: "Temp",
            tokens: { colors: {} },
          });
          throw new Error("boom");
        },
      },
    };
    await expect(host.load(faulty)).rejects.toBeInstanceOf(PluginActivationError);
    // Rolled back: the theme it registered before throwing is gone; host has no plugin.
    expect(targets.themes.some((t) => t.id === "temp")).toBe(false);
    expect(host.isLoaded("faulty")).toBe(false);
  });

  it("denies capabilities not granted by the manifest", async () => {
    const { host, targets } = makeHost();
    const overreaching: LoadablePlugin = {
      manifest: {
        id: "overreach",
        name: "Overreach",
        version: "1.0.0",
        engine: { minimumVersion: "0.1.0" },
        permissions: ["register-themes"], // NOT register-components
      },
      plugin: {
        activate(api) {
          api.registerComponent({
            type: "hacky",
            displayName: "Hacky",
            category: "shape",
            propsSchema: z.object({}).passthrough(),
            defaultProps: {},
            defaultTransform: {},
            render: () => null,
          });
        },
      },
    };
    await expect(host.load(overreaching)).rejects.toThrow(/permission/i);
    expect(targets.components.has("hacky")).toBe(false);
  });
});
