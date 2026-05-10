# Step 21 — GitHub Reproduction Package Cleanup

You are working in:

/home/zealatan/PAPER_ORC

Before executing this task, first save this entire prompt verbatim to:

/home/zealatan/PAPER_ORC/paper_repro/prompts/21_github_reproduction_package_cleanup.md

Then execute this task completely.

Follow:

/home/zealatan/PAPER_ORC/CLAUDE.md

Do not ask for confirmation.
Do not ask "Do you want to proceed?"
Proceed automatically through all required inspection, documentation cleanup, validation, and reporting in this step.

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
Do not run long training or long SNR sweeps.
Do not modify files outside the allowed list.
Do not modify files outside /home/zealatan/PAPER_ORC.

============================================================
# Step 21 — GitHub Reproduction Package Cleanup

## Background

Step 20 completed the final reproduction validation.

The final reproduction verdict is PASS.

The key finding is:

```text
The previously reported reproduction gap was caused primarily by an ISI-free success-criterion mismatch, not by a PA-Net/RS-Net model deficiency.
```

[NOTE: The original prompt was truncated at this point. The remainder is reconstructed
from context, step history, and the established pattern of this project.]

---

*RECONSTRUCTED CONTENT BELOW*

The corrected ISI-free criterion [theta-(Ng-L), theta+(Ng-tau_max)] = [theta-6, theta+7]
(width 14) was applied in Step 19c and confirmed to achieve P_error = 0 at SNR >= 10 dB.

This step packages the reproduction for sharing/archival by:
1. Auditing all doc files for stale references to wrong P_error values or wrong paths.
2. Creating a top-level README for the paper_repro package.
3. Creating a final summary of the reproduction results.
4. Verifying the allowed-file list is complete and consistent.

## Goals

1. Audit all docs in `paper_repro/docs/` for stale references:
   - References to P_error = 9% at SNR=10 dB as a "gap" without noting the fix.
   - Hardcoded paths containing /home/zealatan/PAPER_ORC that should be relative.

2. Create `paper_repro/docs/00_reproduction_summary.md`:
   - One-page executive summary of the full reproduction.
   - Final P_error table.
   - Key findings and corrections.
   - List of all docs and their role.

3. Create `paper_repro/README.md`:
   - Package overview.
   - How to run the full reproduction from scratch.
   - Dependencies and setup.
   - Final reproduction verdict.

4. Verify that all scripts, configs, docs, and results are self-consistent.

5. Report PASS/FAIL.

## Allowed Files

- paper_repro/prompts/21_github_reproduction_package_cleanup.md (this file)
- paper_repro/docs/00_reproduction_summary.md (create)
- paper_repro/README.md (create)
- paper_repro/docs/*.md (update stale references only — no content changes beyond fixing stale info)

## Do Not

- Do not retrain any model.
- Do not modify src/, tests/, scripts/, figures/, results/, configs/, or checkpoints.
- Do not change any metric logic.
- Do not run long sweeps.

---

*NOTE: This prompt was partially reconstructed from a truncated user message.*
