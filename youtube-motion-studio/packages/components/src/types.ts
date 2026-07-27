/**
 * Component definition + registry contracts (spec §8.1, §8.2). A component maps a
 * {@link MotionElement} to backend-agnostic {@link DrawNode} primitives, declares a Zod props
 * schema, default props, and a default transform.
 *
 * `propsSchema` is intentionally a loose `ZodTypeAny`: a component's props schema commonly uses
 * `.default()`/`.optional()`, so its Zod *input* type differs from its *output* type `TProps`.
 * We only care about the validated output, so `readProps` narrows the parsed result to `TProps`.
 */
import type { MotionElement, Transform2D } from "@motion-studio/core";
import type { DrawNode, RenderContext } from "@motion-studio/renderer-core";
import type { ZodTypeAny } from "zod";

export interface ComponentDefinition<TProps = Record<string, unknown>> {
  type: string;
  displayName: string;
  category: "text" | "shape" | "media" | "layout" | "social" | "finance" | "chart";
  icon?: string;
  propsSchema: ZodTypeAny;
  defaultProps: TProps;
  defaultTransform: Partial<Transform2D>;
  /** Render this element's own visual. Children are composited by the frame renderer. */
  render(element: MotionElement, ctx: RenderContext): DrawNode | null;
}

export interface ComponentRegistry {
  register(definition: ComponentDefinition<unknown>): void;
  unregister(type: string): void;
  get(type: string): ComponentDefinition<unknown> | undefined;
  has(type: string): boolean;
  list(): ComponentDefinition<unknown>[];
  listByCategory(category: string): ComponentDefinition<unknown>[];
}

/**
 * Read validated props with a fallback. Components keep working on unknown/invalid props
 * (spec §8.2) rather than throwing.
 */
export function readProps<TProps>(
  definition: ComponentDefinition<TProps>,
  element: MotionElement,
): TProps {
  const parsed = definition.propsSchema.safeParse(element.props);
  return parsed.success ? (parsed.data as TProps) : definition.defaultProps;
}
