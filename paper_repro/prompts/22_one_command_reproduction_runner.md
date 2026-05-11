# Step 22 — One-Command Reproduction Runner and Artifact Manifest

You are working in:

/home/zealatan/PAPER_ORC

Before executing this task, first save this entire prompt verbatim to:

/home/zealatan/PAPER_ORC/paper_repro/prompts/22_one_command_reproduction_runner.md

Then execute this task completely.

Follow:

/home/zealatan/PAPER_ORC/CLAUDE.md

Do not ask for confirmation.
Do not ask "Do you want to proceed?"
Proceed automatically through all required inspection, scripting, validation, documentation, and reporting in this step.

If a check fails:
1. Inspect the failure.
2. Fix only the allowed files.
3. Re-run the failing command.
4. Continue until the step passes or until the issue cannot be fixed within the allowed files.

Do not retrain PA-Net.
Do not retrain RS-Net.
Do not modify checkpoints.
Do not modify model architecture.
Do not modify dataset generation.
Do not change metric logic.
Do not run long training or full paper-scale SNR sweeps.
Do not modify files outside the allowed list.
Do not modify files outside /home/zealatan/PAPER_ORC.

============================================================
# Step 22 — One-Command Reproduction Runner and Artifact Manifest

## Background

Step 20 completed final reproduction validation with all checks passing.
Step 21 completed GitHub-facing package cleanup with all checks passing.

The repository now has a validated reproduction result:

```text
Final status: PASS — reproduction successful after correcting the ISI-free success criterion.
```

[NOTE: The original prompt was truncated at this point. The remainder is reconstructed
from context, step history, and the established pattern of this project.]

---

*RECONSTRUCTED CONTENT BELOW*

## Goals

1. Create `paper_repro/scripts/reproduce.py` — a single script that:
   - Checks all required checkpoints exist (does NOT retrain).
   - Runs the metric unit tests to confirm the criterion is correct.
   - Runs the Fig. 2 sweep (using the already-trained checkpoints).
   - Generates the Fig. 2 figure.
   - Prints a final PASS/FAIL summary.

2. Create `paper_repro/docs/19_artifact_manifest.md`:
   - Lists every key output artifact (checkpoints, CSVs, JSONs, figures, docs).
   - Records file size and existence status.
   - Notes which step produced each file.

3. Run `reproduce.py` and confirm it exits with code 0.

4. Report PASS/FAIL.

## Allowed Files

- paper_repro/prompts/22_one_command_reproduction_runner.md (this file)
- paper_repro/scripts/reproduce.py (create)
- paper_repro/docs/19_artifact_manifest.md (create)

## Do Not

- Do not retrain any model.
- Do not modify checkpoints.
- Do not run full paper-scale training.
- Do not modify src/, tests/, configs/, or existing docs/.

---

*NOTE: This prompt was partially reconstructed from a truncated user message.*
