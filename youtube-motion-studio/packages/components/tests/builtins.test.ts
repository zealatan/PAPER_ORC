import { describe, expect, it } from "vitest";
import { BUILTIN_COMPONENTS, createDefaultComponentRegistry } from "../src";
import { makeContext, makeElement } from "./helpers";

const ctx = makeContext();

describe("built-in component pack (M7)", () => {
  it("registers every built-in component", () => {
    const registry = createDefaultComponentRegistry();
    expect(registry.list().length).toBe(BUILTIN_COMPONENTS.length);
    expect(BUILTIN_COMPONENTS.length).toBeGreaterThanOrEqual(18);
    for (const component of BUILTIN_COMPONENTS) {
      expect(registry.get(component.type)).toBeDefined();
    }
  });

  it("each component has a schema, defaults and a default transform", () => {
    for (const component of BUILTIN_COMPONENTS) {
      expect(component.type).toBeTruthy();
      expect(component.displayName).toBeTruthy();
      expect(component.propsSchema).toBeDefined();
      expect(component.defaultProps).toBeDefined();
      expect(component.defaultTransform).toBeDefined();
    }
  });

  it("renders with default props without crashing", () => {
    for (const component of BUILTIN_COMPONENTS) {
      const element = makeElement(component.type, component.type, {
        transform: { width: 600, height: 400 },
      });
      expect(() => component.render(element, ctx)).not.toThrow();
    }
  });

  it("does not crash on unknown / garbage props", () => {
    for (const component of BUILTIN_COMPONENTS) {
      const element = makeElement(component.type, component.type, {
        transform: { width: 600, height: 400 },
        props: { nonsense: 123, values: "not-an-array", rows: null },
      });
      expect(() => component.render(element, ctx)).not.toThrow();
    }
  });
});
