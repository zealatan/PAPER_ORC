/**
 * Normalize the PG deck's inline markup into plain display text:
 *  - `<b>…</b>` / other tags → stripped
 *  - `|` → line break marker (rendered as a space here; the deck used it for manual wraps)
 *  - `[emphasis]` → the inner text (deck used brackets to colour a run)
 *  - `{{pg}}` → "P&G" (a deck variable)
 */
export function normalizeDeckText(input: unknown): string {
  if (typeof input !== "string") return "";
  return input
    .replace(/\{\{\s*pg\s*\}\}/gi, "P&G")
    .replace(/<[^>]+>/g, "")
    .replace(/\[([^\]]*)\]/g, "$1")
    .replace(/\s*\|\s*/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

/** Join an array of deck text lines into one normalized string. */
export function normalizeDeckLines(lines: unknown): string {
  if (!Array.isArray(lines)) return "";
  return lines
    .map((l) => normalizeDeckText(l))
    .filter(Boolean)
    .join("  ·  ");
}
