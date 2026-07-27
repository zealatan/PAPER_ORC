/**
 * Template packaging (spec §18). Templates are immutable originals; creating from a template makes
 * a **new independent project** (deep-cloned, fresh id + timestamps). Template *content* lives in
 * the app; core only owns the type and the instantiation contract.
 */
import type { MotionProject } from "../project/types";

export interface MotionTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  thumbnailAssetId?: string;
  project: MotionProject;
}

/** Create a new, independent project from a template. Never mutates the template. */
export function instantiateTemplate(
  template: MotionTemplate,
  newId: string,
  now: string,
): MotionProject {
  const project = structuredClone(template.project);
  return {
    ...project,
    id: newId,
    name: template.name,
    createdAt: now,
    updatedAt: now,
  };
}
