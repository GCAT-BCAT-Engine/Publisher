# Publisher to Site Verification Tracker

## Objective

Track the operational verification of the Publisher-to-Site mirror path after policy, dispatch automation, activation-runner, release-gate, Site handoff, Publisher handoff, and automated receipt artifacts were added.

## Status

```text
status: pending_automated_dispatch
```

## Automated Receipt Path

The Publisher dispatch workflow now writes verification receipts automatically using:

```text
tools/write_verification_run_receipt.py
```

The receipt is uploaded as a workflow artifact matching:

```text
publisher-site-verification-receipt-<run>-<attempt>
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
[ ] Site: update docs/SITE_MIRROR_EVIDENCE_PACKET.md with real evidence values.
[ ] Site: update docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json with matching real evidence values.
[ ] Site: run python scripts/check_site_mirror_evidence_packet.py.
[ ] Site: run python scripts/check_site_mirror_live_evidence_state.py.
[ ] Publisher: update docs/verification-tracker.md from pending_automated_dispatch to activated.
[ ] Publisher: update docs/activation-status.md to activated after evidence is recorded.
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
site_evidence_packet_completion_commit: PENDING
site_live_evidence_state_completion_commit: PENDING
publisher_verification_tracker_activation_commit: PENDING
publisher_activation_status_update_commit: PENDING
```

## Release Gate

Do not mark Site paper display current until every applicable check in `docs/release-gate-checklist.md` passes and both Site evidence validators pass.

## Relevant Files

```text
.github/workflows/dispatch-site-mirror.yml
.github/workflows/validate-emergency-ai-cases.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/write_verification_run_receipt.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/site-paper-display-policy.md
docs/validation.md
docs/verification-run-receipt.template.json
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
```

## Next Action

```text
Allow the push-triggered Dispatch Site Paper Mirror workflow to produce the Publisher verification receipt artifact, then use the artifact and Site workflow evidence to complete the Site evidence files and activation closure.
```

## Archive Readiness

This tracker contains the automated mirror verification sequence and evidence fields needed for the next workflow-running session. Older chat context is not required once this file and docs/PUBLISHER_MIRROR_HANDOFF.md are present in the repository.
