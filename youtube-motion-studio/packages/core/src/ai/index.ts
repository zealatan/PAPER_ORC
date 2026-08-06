/**
 * AI draft integration (spec §25). AI never touches rendered nodes — it produces *data*
 * (a project draft, edits, variable values, asset requests) which is always validated before it can
 * affect anything. Invalid AI output is rejected safely and never corrupts the current project.
 */
import { ProjectValidationError, type ValidationIssue } from "../errors";
import { importProject } from "../io/importProject";
import {
  addElementToScene,
  findElementById,
  removeElementById,
  updateElementById,
} from "../project/elementOps";
import type { MotionElement, MotionProject } from "../project/types";

// ── Request / response models (spec §25.2, §25.3) ──

export interface AIGenerationRequest {
  prompt: string;
  targetDuration?: number;
  targetTemplateId?: string;
  themeId?: string;
  script?: string;
  constraints?: {
    maxScenes?: number;
    allowedComponentTypes?: string[];
    language?: string;
  };
}

export interface AssetRequest {
  id: string;
  description: string;
  kind: "image" | "video" | "audio" | "other";
}

export interface AIGenerationResponse {
  projectDraft: unknown;
  assetRequests?: AssetRequest[];
  warnings?: string[];
  explanation?: string;
}

export interface AIAdapter {
  generate(request: AIGenerationRequest): Promise<AIGenerationResponse>;
}

// ── Review of a generated project draft ──

export interface AIReview {
  ok: boolean;
  project?: MotionProject;
  issues: ValidationIssue[];
  warnings: string[];
  assetRequests: AssetRequest[];
}

/** Validate an AI project draft through the standard import pipeline without side effects. */
export function reviewAIResponse(response: AIGenerationResponse): AIReview {
  const warnings = response.warnings ?? [];
  const assetRequests = response.assetRequests ?? [];
  try {
    const { project } = importProject(response.projectDraft);
    return { ok: true, project, issues: [], warnings, assetRequests };
  } catch (error) {
    if (error instanceof ProjectValidationError) {
      return { ok: false, issues: error.issues, warnings, assetRequests };
    }
    return {
      ok: false,
      issues: [
        { path: "", message: error instanceof Error ? error.message : String(error) },
      ],
      warnings,
      assetRequests,
    };
  }
}

// ── Structured AI edits (spec §25.5) ──

export type AIEdit =
  | { type: "update-element"; elementId: string; patch: Record<string, unknown> }
  | { type: "set-variable"; variableId: string; value: unknown }
  | { type: "remove-element"; elementId: string }
  | { type: "add-element"; sceneId: string; element: MotionElement };

function setPath(
  target: Record<string, unknown>,
  segments: string[],
  value: unknown,
): Record<string, unknown> {
  const [head, ...rest] = segments;
  if (head === undefined) return target;
  if (rest.length === 0) return { ...target, [head]: value };
  const child = target[head];
  const childObj =
    child && typeof child === "object" ? (child as Record<string, unknown>) : {};
  return { ...target, [head]: setPath(childObj, rest, value) };
}

/** Apply one AI edit, returning a new project (never mutates the input). */
export function applyAIEdit(project: MotionProject, edit: AIEdit): MotionProject {
  switch (edit.type) {
    case "update-element":
      return updateElementById(project, edit.elementId, (element) => {
        let next: Record<string, unknown> = element as unknown as Record<string, unknown>;
        for (const [path, value] of Object.entries(edit.patch)) {
          next = setPath(next, path.split("."), value);
        }
        return next as unknown as MotionElement;
      });
    case "set-variable": {
      const variable = project.variables[edit.variableId];
      if (!variable) return project;
      return {
        ...project,
        variables: {
          ...project.variables,
          [edit.variableId]: { ...variable, value: edit.value },
        },
      };
    }
    case "remove-element":
      return removeElementById(project, edit.elementId);
    case "add-element":
      return addElementToScene(project, edit.sceneId, edit.element);
    default:
      return project;
  }
}

/** Apply a sequence of approved edits. */
export function applyAIEdits(project: MotionProject, edits: AIEdit[]): MotionProject {
  return edits.reduce(applyAIEdit, project);
}

export interface AIEditSummary {
  edit: AIEdit;
  description: string;
  /** Whether the edit targets something that exists (a reviewable, safe-to-apply check). */
  valid: boolean;
}

function summarize(project: MotionProject, edit: AIEdit): AIEditSummary {
  switch (edit.type) {
    case "update-element":
      return {
        edit,
        description: `Update ${edit.elementId}: ${Object.keys(edit.patch).join(", ")}`,
        valid: findElementById(project, edit.elementId) !== null,
      };
    case "set-variable":
      return {
        edit,
        description: `Set variable ${edit.variableId}`,
        valid: project.variables[edit.variableId] !== undefined,
      };
    case "remove-element":
      return {
        edit,
        description: `Remove ${edit.elementId}`,
        valid: findElementById(project, edit.elementId) !== null,
      };
    case "add-element":
      return {
        edit,
        description: `Add ${edit.element.type} to ${edit.sceneId}`,
        valid: project.scenes.some((s) => s.id === edit.sceneId),
      };
    default:
      return { edit, description: "Unknown edit", valid: false };
  }
}

export interface AIEditReview {
  summaries: AIEditSummary[];
  /** Preview project with all *valid* edits applied — for the user to accept or reject. */
  preview: MotionProject;
}

/** Produce a reviewable diff of a batch of AI edits (applies only the valid ones to the preview). */
export function reviewAIEdits(project: MotionProject, edits: AIEdit[]): AIEditReview {
  const summaries = edits.map((edit) => summarize(project, edit));
  const validEdits = summaries.filter((s) => s.valid).map((s) => s.edit);
  return { summaries, preview: applyAIEdits(project, validEdits) };
}
