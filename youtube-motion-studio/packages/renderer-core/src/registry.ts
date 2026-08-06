/**
 * Default {@link RenderRegistry} implementation and a context factory. Unknown element types are
 * not an error: the frame renderer paints a visible placeholder instead (spec §8.2).
 */
import type { AssetReference, MotionProject } from "@motion-studio/core";
import type { ElementRenderer, RenderContext, RenderRegistry } from "./types";

export class DefaultRenderRegistry implements RenderRegistry {
  private readonly byType = new Map<string, ElementRenderer>();

  register(renderer: ElementRenderer): void {
    this.byType.set(renderer.type, renderer);
  }

  unregister(type: string): void {
    this.byType.delete(type);
  }

  get(type: string): ElementRenderer | undefined {
    return this.byType.get(type);
  }

  has(type: string): boolean {
    return this.byType.has(type);
  }

  list(): ElementRenderer[] {
    return [...this.byType.values()];
  }
}

export interface RenderContextOptions {
  time?: number;
  sceneTime?: number;
}

/** Build a render context from a project, resolving assets from its asset list. */
export function createRenderContext(
  project: MotionProject,
  options: RenderContextOptions = {},
): RenderContext {
  const assetsById = new Map<string, AssetReference>(
    project.assets.map((asset) => [asset.id, asset]),
  );

  const resolveAssetUrl = (assetId: string): string | null => {
    const asset = assetsById.get(assetId);
    if (!asset) return null;
    switch (asset.source.kind) {
      case "data-url":
        return asset.source.value;
      case "remote-url":
        return asset.source.url;
      case "local-path":
        return asset.source.path;
      case "object-url":
        return asset.source.key;
      case "generated":
        return null;
      default:
        return null;
    }
  };

  return {
    project,
    time: options.time ?? 0,
    sceneTime: options.sceneTime ?? 0,
    resolveAssetUrl,
    getAsset: (assetId) => assetsById.get(assetId),
  };
}
