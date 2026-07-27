/**
 * Default {@link ComponentRegistry} and a bridge that installs component renderers into a
 * renderer-core {@link RenderRegistry}.
 */
import type { RenderRegistry } from "@motion-studio/renderer-core";
import type { ComponentDefinition, ComponentRegistry } from "./types";

export class DefaultComponentRegistry implements ComponentRegistry {
  private readonly byType = new Map<string, ComponentDefinition<unknown>>();

  register(definition: ComponentDefinition<unknown>): void {
    this.byType.set(definition.type, definition);
  }

  unregister(type: string): void {
    this.byType.delete(type);
  }

  get(type: string): ComponentDefinition<unknown> | undefined {
    return this.byType.get(type);
  }

  has(type: string): boolean {
    return this.byType.has(type);
  }

  list(): ComponentDefinition<unknown>[] {
    return [...this.byType.values()];
  }

  listByCategory(category: string): ComponentDefinition<unknown>[] {
    return this.list().filter((definition) => definition.category === category);
  }
}

/** Install every component in a component registry as an element renderer. */
export function installRenderers(
  components: ComponentRegistry,
  renderers: RenderRegistry,
): void {
  for (const definition of components.list()) {
    renderers.register({
      type: definition.type,
      render: (element, ctx) => definition.render(element, ctx),
    });
  }
}
