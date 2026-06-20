# Publisher to Site Verification Tracker

## Objective

Track the operational verification of the Publisher-to-Site mirror path after policy, dispatch automation, activation-runner, release-gate, Site handoff, Publisher handoff, automated receipt artifacts, and Publisher closure evidence production were added.

## Status

```text
status: pending_fresh_ordered_artifacts
last_automation_nudge_utc: 2026-06-18T05:38:00Z
nudge_reason: continue_without_manual_actions_through_completion
activation_boundary: Publisher closure evidence production
```

## Automated Receipt Path

The Publisher dispatch workflow writes verification receipts automatically using:

```text
tools/write_verification_run_receipt.py
```

The receipt is uploaded as a workflow artifact matching:

```text
publisher-site-verification-receipt-<run>-<attempt>
```

## Closure Evidence Production Path

Publisher closure evidence production is defined by:

```text
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
tools/check_publisher_closure_evidence_production.py
tools/close_site_mirror_activation.py
github/workflows/close-site-mirror-activation.yml
```

Activation remains pending until both required artifact classes are fresh, ordered, and evidence-valid:

```text
publisher-site-verification-receipt-<run>-<attempt>
site-mirror-evidence-<run>-<attempt>
MAX_ARTIFACT_AGE_HOURS: 48
ORDER_GRACE_MINUTES: 5
```

## Verification Receipt Template

The baseline receipt shape remains documented in:

```text
docs/verification-run-receipt.template.json
```

## Required Verification Sequence

```text
[ ] Publisher: qualifying push to main triggers Dispatch Site Paper Mirror.
[ ] Publisher workflow: installs validator dependencies.
[ ] Publisher workflow: runs python tools/check_publisher_activation.py.
[ ] Publisher workflow: confirms activation validation prints valid: Publisher activation checks.
[ ] Publisher workflow: resolves Site repository and Publisher source ref.
[ ] Publisher workflow: confirms dispatch credentials are configured without exposing values.
[ ] Publisher workflow: dispatches Site mirror workflow when validation passes.
[ ] Publisher workflow: writes verification receipt using tools/write_verification_run_receipt.py.
[ ] Publisher workflow: uploads publisher-site-verification-receipt artifact.
[ ] Site: Mirror Papers from Publisher workflow starts and completes.
[ ] Site: capture Site mirror workflow URL.
[ ] Site: capture Site mirror commit SHA.
[ ] Site: confirm papers/papers_manifest.json includes source metadata.
[ ] Site: confirm public aliases resolve.
[ ] Site: Site evidence artifact is uploaded as site-mirror-evidence-<run>-<attempt>.
[ ] Publisher: close-site-mirror-activation workflow runs tools/check_publisher_closure_evidence_production.py.
[ ] Publisher: closure updater verifies freshness and ordering.
[ ] Publisher: closure updater writes a pending probe or activation closure receipt.
[ ] Publisher: verification tracker is updated to activated only from closure receipt evidence.
[ ] Publisher: activation status is updated to activated only from closure receipt evidence.
```

## Evidence Fields To Capture

```text
publisher_workflow_run_url: PENDING
publisher_verification_receipt_artifact: PENDING
publisher_live_dispatch_workflow_url: PENDING
site_mirror_workflow_url: PENDING
site_mirror_commit_sha: PENDING
manifest_source_repository: PENDING
manifest_source_ref: PENDING
manifest_source_of_truth: PENDING
alias_verification_results: PENDING
site_evidence_artifact: PENDING
publisher_pending_probe: docs/mirror-activation-closures/publisher-site-mirror-pending.json
publisher_activation_closure_receipt: PENDING
publisher_verification_tracker_activation_commit: PENDING
publisher_activation_status_update_commit: PENDING
```

## Release Gate

Do not mark Site paper display current until every applicable check in `docs/release-gate-checklist.md` passes and the Publisher closure evidence gate has produced a closure receipt.

The pending probe is not an activation receipt.

## Relevant Files

```text
.github/workflows/dispatch-site-mirror.yml
.github/workflows/close-site-mirror-activation.yml
.github/workflows/validate-emergency-ai-cases.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
tools/check_publisher_mirror_handoff.py
tools/check_mirror_ecosystem_management_handoff.py
tools/check_publisher_closure_evidence_production.py
tools/write_verification_run_receipt.py
tools/close_site_mirror_activation.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/site-paper-display-policy.md
docs/validation.md
docs/verification-run-receipt.template.json
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
```

## Next Action

```text
Let the automated workflows proceed: Publisher dispatch produces a fresh Publisher receipt artifact, Site mirror produces a fresh Site evidence artifact, and Publisher closure workflow commits activation when both artifact classes are fresh, ordered, and evidence-valid.
```

## Archive Readiness

This tracker contains the automated mirror verification sequence, closure evidence production boundary, evidence fields, pending probe reference, and activation blockers needed for the next workflow-running session. Older chat context is not required once this file and docs/PUBLISHER_MIRROR_HANDOFF.md are present in the repository.
