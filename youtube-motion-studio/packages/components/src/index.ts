/**
 * @motion-studio/components — the built-in component pack (text, shapes, media, layout) and the
 * registries that wire them into the renderer.
 */
import { DefaultRenderRegistry, type RenderRegistry } from "@motion-studio/renderer-core";
import { DefaultComponentRegistry, installRenderers } from "./registry";
import type { ComponentDefinition, ComponentRegistry } from "./types";
import { rectangleComponent } from "./shapes/rectangle";
import { circleComponent } from "./shapes/circle";
import { textComponent } from "./text/text";
import { imageComponent } from "./media/image";
import { groupComponent } from "./layout/group";

export * from "./types";
export { DefaultComponentRegistry, installRenderers } from "./registry";
export { rectangleComponent } from "./shapes/rectangle";
export { circleComponent } from "./shapes/circle";
export { textComponent } from "./text/text";
export { imageComponent } from "./media/image";
export { groupComponent } from "./layout/group";

/** Every built-in component definition, in registration order. */
export const BUILTIN_COMPONENTS: ComponentDefinition<unknown>[] = [
  rectangleComponent,
  circleComponent,
  textComponent,
  imageComponent,
  groupComponent,
];

/** A component registry pre-populated with the built-in components. */
export function createDefaultComponentRegistry(): ComponentRegistry {
  const registry = new DefaultComponentRegistry();
  for (const component of BUILTIN_COMPONENTS) {
    registry.register(component);
  }
  return registry;
}

/** A renderer-core RenderRegistry with the built-in components installed as element renderers. */
export function createDefaultRenderRegistry(): RenderRegistry {
  const renderers = new DefaultRenderRegistry();
  installRenderers(createDefaultComponentRegistry(), renderers);
  return renderers;
}
