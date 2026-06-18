# Publisher Mirror Handoff

## Purpose

This handoff lets a Publisher-side build session continue Publisher-to-Site mirror activation without needing prior chat context.

Use this file as the Publisher-side source of truth for mirror dispatch continuation.

## Current Goal

```text
Goal: Publisher-to-Site mirror dispatch activation
Repository: GCAT-BCAT-Engine/Publisher
Target repository: StegVerse-Labs/Site
Source path: papers
Target path: papers
Activation state: ready_for_automated_push_dispatch
```

## Built Files

```text
github/workflows/dispatch-site-mirror.yml
github/workflows/validate-emergency-ai-cases.yml
github/workflows/generate-papers.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
tools/write_verification_run_receipt.py
docs/site-paper-display-policy.md
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/validation.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/verification-tracker.md
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.

## Publisher Mirror Contract

Publisher remains the source of truth. Site remains the public display surface.

Publisher may dispatch Site only after Publisher activation validation passes.

The Publisher dispatch workflow is displayed as:

```text
github/workflows/dispatch-site-mirror.yml
```

The actual repository path includes the leading dot.

The Publisher generate workflow is displayed as:

```text
github/workflows/generate-papers.yml
```

The actual repository path includes the leading dot.

The target Site workflow is displayed as:

```text
StegVerse-Labs/Site/github/workflows/mirror-papers.yml
```

The actual Site repository path includes the leading dot.

## Automated Activation Sequence

The preferred activation path is push-triggered automation. A workflow-dispatch dry run remains available as an optional diagnostic fallback, but forward activation no longer depends on a manual dry-run step.

```text
1. Publisher: a qualifying push to main triggers Dispatch Site Paper Mirror.
2. Publisher workflow: checks out Publisher.
3. Publisher workflow: installs validator dependencies.
4. Publisher workflow: runs python tools/check_publisher_activation.py.
5. Publisher workflow: resolves target Site repository and source ref.
6. Publisher workflow: verifies dispatch credentials are available without exposing values.
7. Publisher workflow: dispatches the Site mirror workflow when validation and credential checks pass.
8. Publisher workflow: writes a verification receipt using tools/write_verification_run_receipt.py.
9. Publisher workflow: uploads the receipt as a workflow artifact named publisher-site-verification-receipt-<run>-<attempt>.
10. Site workflow: mirrors papers from Publisher.
11. Site workflow: validates manifest metadata and aliases.
12. Site workflow or follow-up automation: completes Site evidence packet and live evidence state from captured workflow evidence.
13. Site validators: run python scripts/check_site_mirror_evidence_packet.py and python scripts/check_site_mirror_live_evidence_state.py.
14. Publisher automation or follow-up governed commit: updates docs/verification-tracker.md from pending_automated_dispatch to activated after evidence is complete.
15. Publisher automation or follow-up governed commit: updates docs/activation-status.md to activated after evidence is complete.
```

## Required Validation Command

Before dispatch completion, Publisher runs:

```text
python tools/check_publisher_activation.py
```

The activation runner includes:

```text
tools/check_emergency_ai_templates.py
tools/validate_emergency_ai_cases.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
```

The Site mirror dispatch checker now also requires the automated receipt writer and workflow artifact upload path.

## Evidence To Capture Automatically Or By Governed Follow-Up

```text
Publisher workflow run URL
Publisher verification receipt artifact
Publisher live dispatch workflow URL
Site mirror workflow URL
Site mirror commit SHA
papers/papers_manifest.json source_repository
papers/papers_manifest.json source_ref
papers/papers_manifest.json source_of_truth
public alias verification results
Site evidence packet completion commit
Site live evidence state completion commit
Publisher verification tracker activation commit
Publisher activation-status update commit
```

## Cross-Repo Evidence Gate

Publisher activation must not be marked activated until both Site evidence files are complete and their validators pass:

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
python scripts/check_site_mirror_evidence_packet.py
python scripts/check_site_mirror_live_evidence_state.py
```

This prevents Publisher from claiming live dispatch activation while Site still contains pending evidence placeholders.

## Current Delta

```text
Resolved: Publisher validation, release gate, dispatch protocol, dry-run mode, receipt template, and verification tracker exist.
Resolved: Publisher handoff records the Generate Papers JSON workflow and its checker as part of the activation runner.
Resolved: Site checked-in papers/papers_manifest.json now includes required source metadata.
Resolved: Publisher handoff separates validation, dispatch credential confirmation, live dispatch, Site evidence capture, Site evidence validation, verification tracker activation, and activation-status update.
Resolved: Publisher handoff requires Site live evidence state completion and validation before Publisher activation is marked activated.
Resolved: Publisher dispatch workflow now generates verification receipt artifacts automatically using tools/write_verification_run_receipt.py.
Pending: automated Publisher dispatch run evidence, Publisher receipt artifact, Site workflow evidence, alias verification, Site evidence packet completion, Site live evidence state completion, verification tracker activation, and activation-status update.
```

## Companion Site Handoff

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
```

## Archive Readiness

This handoff contains the Publisher repo state, automated activation sequence, and evidence requirements needed to continue. Prior chat thread context is not required for forward progress once this file is present in the repository.
