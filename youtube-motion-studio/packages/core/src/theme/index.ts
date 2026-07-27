/**
 * Theme engine (spec §10). A theme is a set of design tokens. Element style/props values that
 * reference a token with the `token:<name>` convention are resolved to the theme's value at render
 * time, so switching themes updates every token-bound component. Manual (non-token) values are
 * preserved (spec §10.3).
 */
import type { MotionElement, MotionProject } from "../project/types";

export interface Theme {
  id: string;
  name: string;
  tokens: {
    colors: Record<string, string>;
  };
}

export const THEMES: Theme[] = [
  {
    id: "minimal-dark",
    name: "Minimal Dark",
    tokens: {
      colors: {
        background: "#0f1115",
        surface: "#1e222b",
        text: "#ffffff",
        textSecondary: "#9aa3b2",
        accent: "#4aa3ff",
      },
    },
  },
  {
    id: "finance-yellow",
    name: "Finance Yellow",
    tokens: {
      colors: {
        background: "#0b0e14",
        surface: "#161a22",
        text: "#ffffff",
        textSecondary: "#c9c39a",
        accent: "#ffd000",
      },
    },
  },
  {
    id: "corporate-blue",
    name: "Corporate Blue",
    tokens: {
      colors: {
        background: "#0a1a2f",
        surface: "#12283f",
        text: "#eaf2fb",
        textSecondary: "#9fb6cf",
        accent: "#2f80ed",
      },
    },
  },
  {
    id: "news-red",
    name: "News Red",
    tokens: {
      colors: {
        background: "#140a0a",
        surface: "#241010",
        text: "#fff5f5",
        textSecondary: "#d0a3a3",
        accent: "#e01e37",
      },
    },
  },
  {
    id: "clean-white",
    name: "Clean White",
    tokens: {
      colors: {
        background: "#ffffff",
        surface: "#f2f2f4",
        text: "#111111",
        textSecondary: "#666666",
        accent: "#111111",
      },
    },
  },
];

export const DEFAULT_THEME_ID = "minimal-dark";

export function resolveTheme(themeId: string): Theme {
  return THEMES.find((theme) => theme.id === themeId) ?? THEMES[0]!;
}

const TOKEN_PREFIX = "token:";

function resolveValue(value: unknown, theme: Theme): unknown {
  if (typeof value === "string" && value.startsWith(TOKEN_PREFIX)) {
    const token = value.slice(TOKEN_PREFIX.length);
    return theme.tokens.colors[token] ?? value;
  }
  return value;
}

function resolveBag(bag: Record<string, unknown>, theme: Theme): Record<string, unknown> {
  let changed = false;
  const next: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(bag)) {
    const resolved = resolveValue(value, theme);
    if (resolved !== value) changed = true;
    next[key] = resolved;
  }
  return changed ? next : bag;
}

function themeElement(element: MotionElement, theme: Theme): MotionElement {
  const style = resolveBag(element.style, theme);
  const props = resolveBag(element.props, theme);
  const children = element.children?.map((c) => themeElement(c, theme));
  if (style === element.style && props === element.props && !children) return element;
  return { ...element, style, props, ...(children ? { children } : {}) };
}

/** Return a project with `token:<name>` references resolved against the given theme. */
export function applyTheme(project: MotionProject, theme: Theme): MotionProject {
  return {
    ...project,
    scenes: project.scenes.map((scene) => ({
      ...scene,
      elements: scene.elements.map((el) => themeElement(el, theme)),
    })),
  };
}
