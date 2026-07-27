import { describe, expect, it } from "vitest";
import {
  applyAIEdit,
  findElementById,
  reviewAIEdits,
  reviewAIResponse,
  ronaldReadProject,
  type AIEdit,
} from "../src";

describe("reviewAIResponse", () => {
  it("accepts a valid project draft as editable data", () => {
    const review = reviewAIResponse({
      projectDraft: ronaldReadProject,
      warnings: ["auto-generated"],
      assetRequests: [{ id: "logo", description: "Company logo", kind: "image" }],
    });
    expect(review.ok).toBe(true);
    expect(review.project?.id).toBe("project-example-001");
    expect(review.warnings).toContain("auto-generated");
    expect(review.assetRequests).toHaveLength(1);
  });

  it("rejects invalid AI output safely (no throw, structured issues)", () => {
    const review = reviewAIResponse({ projectDraft: { schemaVersion: "1.0.0" } });
    expect(review.ok).toBe(false);
    expect(review.project).toBeUndefined();
    expect(review.issues.length).toBeGreaterThan(0);
  });

  it("rejects a non-object draft without throwing", () => {
    expect(() => reviewAIResponse({ projectDraft: 42 })).not.toThrow();
    expect(reviewAIResponse({ projectDraft: 42 }).ok).toBe(false);
  });
});

describe("AI edits", () => {
  it("applies an update-element edit as a patch", () => {
    const edit: AIEdit = {
      type: "update-element",
      elementId: "caption-1",
      patch: { "props.text": "새로운 제목" },
    };
    const next = applyAIEdit(ronaldReadProject, edit);
    expect(findElementById(next, "caption-1")?.element.props.text).toBe("새로운 제목");
    // original untouched
    expect(findElementById(ronaldReadProject, "caption-1")?.element.props.text).not.toBe(
      "새로운 제목",
    );
  });

  it("reviews a batch, marking invalid edits and applying only valid ones", () => {
    const edits: AIEdit[] = [
      { type: "update-element", elementId: "caption-1", patch: { "props.text": "OK" } },
      {
        type: "update-element",
        elementId: "does-not-exist",
        patch: { "props.text": "X" },
      },
      { type: "set-variable", variableId: "person_name", value: "Warren Buffett" },
    ];
    const review = reviewAIEdits(ronaldReadProject, edits);
    expect(review.summaries.map((s) => s.valid)).toEqual([true, false, true]);
    expect(findElementById(review.preview, "caption-1")?.element.props.text).toBe("OK");
    expect(review.preview.variables.person_name?.value).toBe("Warren Buffett");
  });
});
