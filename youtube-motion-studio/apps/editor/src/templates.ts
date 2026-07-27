/**
 * Starter templates (content — spec §0: content lives in the app, not the engine). Each is a
 * reusable `MotionTemplate` whose project uses variable bindings (edit once → updates everywhere)
 * and `token:` theme references (switch theme → restyles).
 */
import {
  DEFAULT_TRANSFORM,
  createEmptyProject,
  type MotionElement,
  type MotionProject,
  type MotionTemplate,
  type Transform2D,
  type VariableBinding,
} from "@motion-studio/core";

function t(o: Partial<Transform2D>): Transform2D {
  return { ...DEFAULT_TRANSFORM, anchorX: 0, anchorY: 0, ...o };
}

function el(
  id: string,
  type: string,
  box: Partial<Transform2D>,
  props: Record<string, unknown>,
  bindings?: VariableBinding[],
): MotionElement {
  return {
    id,
    type,
    name: id,
    visible: true,
    locked: false,
    transform: t({ zIndex: 1, ...box }),
    style: {},
    props,
    timing: { start: 0, duration: 5 },
    animations: [],
    ...(bindings ? { bindings } : {}),
  };
}

function base(name: string): MotionProject {
  return createEmptyProject({ id: "template", name, now: "2026-01-01T00:00:00.000Z" });
}

const biography: MotionTemplate = {
  id: "biography-story",
  name: "Biography Story",
  description: "Profile intro with a headline and a bound name.",
  category: "story",
  project: {
    ...base("Biography Story"),
    theme: { themeId: "finance-yellow" },
    variables: {
      person_name: {
        id: "person_name",
        name: "Person Name",
        type: "string",
        value: "Ronald Read",
      },
      headline: {
        id: "headline",
        name: "Headline",
        type: "string",
        value: "아무도 그를 부자라고 생각하지 않았음.",
      },
    },
    scenes: [
      {
        id: "scene-1",
        name: "Intro",
        duration: 5,
        background: { type: "solid", color: "#0b0e14" },
        elements: [
          el(
            "title",
            "title",
            { x: 90, y: 120, width: 900, height: 150, zIndex: 2 },
            {
              text: "Biography",
              fontSize: 72,
              color: "token:accent",
            },
          ),
          el(
            "card",
            "profile-card",
            { x: 90, y: 700, width: 900, height: 260, zIndex: 2 },
            { title: "Name", subtitle: "Investor", background: "token:surface" },
            [{ variableId: "person_name", targetPath: "props.title" }],
          ),
          el(
            "caption",
            "caption",
            { x: 90, y: 1650, width: 900, height: 120, zIndex: 3 },
            { text: "Headline", fontSize: 44, background: "token:surface" },
            [{ variableId: "headline", targetPath: "props.text" }],
          ),
        ],
      },
    ],
  },
};

const statCard: MotionTemplate = {
  id: "stat-card",
  name: "Stat Card",
  description: "A single big statistic with a label and a bar chart.",
  category: "finance",
  project: {
    ...base("Stat Card"),
    theme: { themeId: "corporate-blue" },
    variables: {
      stat_label: {
        id: "stat_label",
        name: "Label",
        type: "string",
        value: "Dividend Yield",
      },
      stat_value: { id: "stat_value", name: "Value", type: "string", value: "2.96%" },
    },
    scenes: [
      {
        id: "scene-1",
        name: "Stat",
        duration: 5,
        background: { type: "solid", color: "#0a1a2f" },
        elements: [
          el(
            "label",
            "title",
            { x: 90, y: 300, width: 900, height: 120, zIndex: 2 },
            { text: "Label", fontSize: 56, color: "token:textSecondary" },
            [{ variableId: "stat_label", targetPath: "props.text" }],
          ),
          el(
            "value",
            "title",
            { x: 90, y: 440, width: 900, height: 260, zIndex: 2 },
            { text: "0%", fontSize: 180, color: "token:accent" },
            [{ variableId: "stat_value", targetPath: "props.text" }],
          ),
          el(
            "bars",
            "bar-chart",
            { x: 240, y: 900, width: 600, height: 500, zIndex: 2 },
            {
              values: [3, 5, 4, 7, 6, 9],
              color: "token:accent",
            },
          ),
        ],
      },
    ],
  },
};

export const STARTER_TEMPLATES: MotionTemplate[] = [biography, statCard];
