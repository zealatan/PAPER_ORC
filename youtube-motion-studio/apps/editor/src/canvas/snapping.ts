/**
 * Pure snapping engine used during drag (spec §12 snapping guides). Given a moving box, the other
 * boxes, and the canvas bounds, it finds the nearest alignment within `tolerance` on each axis and
 * returns the offset (dx/dy) that aligns them plus the guide lines to draw. No mutation, no state.
 */
import type { ScreenBox } from "../state/projectOps";

export interface Guide {
  axis: "x" | "y";
  position: number; // project pixels
}

export interface SnapResult {
  dx: number;
  dy: number;
  guides: Guide[];
}

interface AxisSnap {
  offset: number;
  target: number | null;
}

/** Best snap on a single axis: smallest |target - moving| within tolerance, else no snap. */
function snapAxis(
  movingLines: number[],
  targetLines: number[],
  tolerance: number,
): AxisSnap {
  let best: AxisSnap = { offset: 0, target: null };
  let bestDelta = tolerance;
  for (const target of targetLines) {
    for (const movingLine of movingLines) {
      const delta = Math.abs(target - movingLine);
      if (delta <= bestDelta) {
        bestDelta = delta;
        best = { offset: target - movingLine, target };
      }
    }
  }
  return best;
}

export function computeSnap(
  moving: ScreenBox,
  others: ScreenBox[],
  canvas: { width: number; height: number },
  tolerance: number,
): SnapResult {
  const movingX = [
    moving.left,
    moving.left + moving.width / 2,
    moving.left + moving.width,
  ];
  const movingY = [
    moving.top,
    moving.top + moving.height / 2,
    moving.top + moving.height,
  ];

  const targetX = [0, canvas.width / 2, canvas.width];
  const targetY = [0, canvas.height / 2, canvas.height];
  for (const box of others) {
    targetX.push(box.left, box.left + box.width / 2, box.left + box.width);
    targetY.push(box.top, box.top + box.height / 2, box.top + box.height);
  }

  const x = snapAxis(movingX, targetX, tolerance);
  const y = snapAxis(movingY, targetY, tolerance);

  const guides: Guide[] = [];
  if (x.target !== null) guides.push({ axis: "x", position: x.target });
  if (y.target !== null) guides.push({ axis: "y", position: y.target });

  return { dx: x.offset, dy: y.offset, guides };
}
