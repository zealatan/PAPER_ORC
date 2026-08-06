/**
 * Variable binding resolution (spec §9). `applyBindings` produces a project where every element's
 * variable bindings have been written into the target path (e.g. `props.title`), so changing a
 * variable value updates every bound element on the next render. Pure and immutable.
 */
import type { MotionElement, MotionProject, VariableBinding } from "./types";

/** Minimal number formatter for binding transforms (e.g. "0.0%"). */
function formatNumber(value: number, format: string): string {
  const decimals = (format.split(".")[1] ?? "").replace(/[^0#]/g, "").length;
  if (format.includes("%")) {
    return `${(value * 100).toFixed(decimals)}%`;
  }
  if (format.includes(",")) {
    return value.toLocaleString("en-US", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  }
  return decimals > 0 ? value.toFixed(decimals) : String(value);
}

function applyTransform(
  value: unknown,
  transform: VariableBinding["transform"],
): unknown {
  if (!transform) return value;
  if (transform.type === "format-number" && typeof value === "number") {
    const format = typeof transform.format === "string" ? transform.format : "0";
    return formatNumber(value, format);
  }
  if (transform.type === "uppercase" && typeof value === "string") {
    return value.toUpperCase();
  }
  return value;
}

/** Immutably set a dotted path (e.g. ["props", "title"]) on an object, cloning along the way. */
function setPath(
  target: Record<string, unknown>,
  segments: string[],
  value: unknown,
): Record<string, unknown> {
  const [head, ...rest] = segments;
  if (head === undefined) return target;
  if (rest.length === 0) {
    return { ...target, [head]: value };
  }
  const child = target[head];
  const childObj =
    child && typeof child === "object" ? (child as Record<string, unknown>) : {};
  return { ...target, [head]: setPath(childObj, rest, value) };
}

function bindElement(
  element: MotionElement,
  variables: MotionProject["variables"],
): MotionElement {
  let next: Record<string, unknown> = element as unknown as Record<string, unknown>;
  for (const binding of element.bindings ?? []) {
    const variable = variables[binding.variableId];
    if (!variable) continue;
    const value = applyTransform(variable.value, binding.transform);
    next = setPath(next, binding.targetPath.split("."), value);
  }
  let bound = next as unknown as MotionElement;
  if (bound.children) {
    bound = { ...bound, children: bound.children.map((c) => bindElement(c, variables)) };
  }
  return bound;
}

/** Return a project with all variable bindings resolved into element props/style. */
export function applyBindings(project: MotionProject): MotionProject {
  const hasBindings = project.scenes.some((scene) =>
    scene.elements.some((el) => (el.bindings?.length ?? 0) > 0 || el.children),
  );
  if (!hasBindings) return project;
  return {
    ...project,
    scenes: project.scenes.map((scene) => ({
      ...scene,
      elements: scene.elements.map((el) => bindElement(el, project.variables)),
    })),
  };
}
