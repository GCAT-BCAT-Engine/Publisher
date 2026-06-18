# Publisher to Site Verification Tracker

## Objective

Track the operational verification of the Publisher-to-Site mirror path after policy, dispatch, dry-run, activation-runner, release-gate, Site handoff, and Publisher handoff checks were added.

## Status

```text
status: pending_dry_run
```

## iPhone Runbook

Use this runbook for the first dry-run test:

```text
docs/iphone-dry-run-runbook.md
```

## Verification Receipt Template

Capture the dry-run or live-dispatch result using:

```text
docs/verification-run-receipt.template.json
```

## Required Verification Sequence

```text
[ ] Publisher: Generate Papers JSON.
[ ] Publisher: Validate Emergency AI Cases.
[ ] Publisher: run python tools/check_publisher_activation.py.
[ ] Publisher: confirm tools/check_publisher_activation.py prints valid: Publisher activation checks.
[ ] Publisher: run Dispatch Site Paper Mirror manually with dry_run: true.
[ ] Publisher: confirm dry run prints that Site mirror dispatch was not attempted.
[ ] Publisher: capture dry-run workflow URL.
[ ] Publisher: capture dry-run receipt commit using docs/verification-run-receipt.template.json.
[ ] Publisher: confirm dispatch credentials are configured.
[ ] Publisher: run Dispatch Site Paper Mirror manually with dry_run: false.
[ ] Publisher: capture live dispatch workflow URL.
[ ] Site: confirm Mirror Papers from Publisher workflow starts and completes.
[ ] Site: capture Site mirror workflow URL.
[ ] Site: capture Site mirror commit SHA.
[ ] Site: confirm papers/papers_manifest.json includes source metadata.
[ ] Site: confirm public aliases resolve.
[ ] Site: update docs/SITE_MIRROR_EVIDENCE_PACKET.md with real evidence values.
[ ] Site: run python scripts/check_site_mirror_evidence_packet.py.
[ ] Publisher: capture live-dispatch receipt commit.
[ ] Publisher: update docs/verification-tracker.md from pending_dry_run to activated.
[ ] Publisher: update docs/activation-status.md to activated after evidence is recorded.
```

## Evidence Fields To Capture

```text
publisher_dry_run_workflow_url: PENDING
publisher_dry_run_receipt_commit: PENDING
publisher_live_dispatch_workflow_url: PENDING
site_mirror_workflow_url: PENDING
site_mirror_commit_sha: PENDING
manifest_source_repository: PENDING
manifest_source_ref: PENDING
manifest_source_of_truth: PENDING
alias_verification_results: PENDING
publisher_live_dispatch_receipt_commit: PENDING
publisher_verification_tracker_activation_commit: PENDING
publisher_activation_status_update_commit: PENDING
```

## Release Gate

Do not mark Site paper display current until every applicable check in `docs/release-gate-checklist.md` passes.

## Relevant Files

```text
.github/workflows/dispatch-site-mirror.yml
.github/workflows/validate-emergency-ai-cases.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/site-paper-display-policy.md
docs/validation.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
```

## Next Action

```text
Run Dispatch Site Paper Mirror manually with dry_run: true, then capture the dry-run workflow URL and dry-run receipt commit before live dispatch.
```

## Archive Readiness

This tracker contains the full mirror verification sequence and evidence fields needed for the next workflow-running session. Older chat context is not required once this file and docs/PUBLISHER_MIRROR_HANDOFF.md are present in the repository.
