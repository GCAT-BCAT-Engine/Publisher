# Publisher Mirror Handoff

## Purpose

This handoff lets a Publisher-side build session continue Publisher-to-Site mirror activation without needing prior chat context.

Use this file as the Publisher-side source of truth for mirror dispatch, automated closure continuation, and ecosystem-management handoff.

## Current Assessment Goal

```text
Continue building without manual actions needed through completion OR until task handoff and task completion is capable of being handled by the ecosystem's own management.
```

## Current Goal

```text
Goal: Publisher closure evidence production
Repository: GCAT-BCAT-Engine/Publisher
Target repository: StegVerse-Labs/Site
Source path: papers
Target path: papers
Activation state: pending_fresh_ordered_artifacts
Completion class: self_managed_handoff_completion
```

## Built Files

```text
github/workflows/dispatch-site-mirror.yml
github/workflows/close-site-mirror-activation.yml
github/workflows/validate-emergency-ai-cases.yml
github/workflows/generate-papers.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
tools/write_verification_run_receipt.py
tools/close_site_mirror_activation.py
tools/check_publisher_mirror_handoff.py
tools/check_mirror_ecosystem_management_handoff.py
tools/check_publisher_closure_evidence_production.py
docs/site-paper-display-policy.md
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/validation.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/verification-tracker.md
docs/activation-status.md
docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
docs/mirror-activation-closures/publisher-site-mirror-pending.json
docs/mirror-activation-closures/<closure>.json
docs/PUBLISHER_MIRROR_HANDOFF.md
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.

## Publisher Mirror Contract

Publisher remains the source of truth. Site remains the public display surface.

Publisher may dispatch Site only after Publisher activation validation passes.

Publisher must not upload a live accepted verification receipt after a failed credential check or failed Site workflow dispatch. The dispatch workflow gates receipt writing and artifact upload with `success()` so only a successful dry run or successful live dispatch can produce a verification receipt artifact.

## Automated Activation Sequence

The preferred activation path is push-triggered automation plus event/scheduled closure retry. A workflow-dispatch dry run remains available as an optional diagnostic fallback, but forward activation no longer depends on a manual dry-run or hand-filled evidence step.

```text
1. Publisher: a qualifying push to main triggers Dispatch Site Paper Mirror.
2. Publisher workflow: runs python tools/check_publisher_activation.py.
3. Publisher workflow: verifies dispatch credentials are available without exposing values.
4. Publisher workflow: dispatches the Site mirror workflow when validation and credential checks pass.
5. Publisher workflow: writes a verification receipt using tools/write_verification_run_receipt.py only after the workflow remains successful.
6. Publisher workflow: uploads the receipt as a workflow artifact named publisher-site-verification-receipt-<run>-<attempt> only after the workflow remains successful.
7. Publisher workflow completion triggers Close Site Mirror Activation through workflow_run.
8. Site workflow: mirrors papers from Publisher.
9. Site workflow: validates manifest metadata and aliases.
10. Site workflow: writes Site evidence using scripts/write_site_mirror_evidence.py.
11. Site workflow: uploads the Site evidence artifact named site-mirror-evidence-<run>-<attempt>.
12. Site workflow nudges Publisher closure when cross-repo credentials are available; scheduled Publisher closure remains fallback.
13. Publisher closure workflow: runs tools/check_publisher_closure_evidence_production.py.
14. Publisher closure workflow: runs tools/close_site_mirror_activation.py with bounded retry.
15. Publisher closure script: rejects stale or out-of-order artifact pairs.
16. Publisher closure script: writes docs/mirror-activation-closures/publisher-site-mirror-pending.json while waiting for fresh ordered artifacts.
17. Publisher closure script: writes docs/mirror-activation-closures/<closure>.json when both artifact classes contain minimum activation evidence and pass freshness/order gates.
18. Publisher closure workflow: updates docs/verification-tracker.md and docs/activation-status.md to activated.
19. Publisher closure workflow: commits pending probe or closure files automatically when changed.
```

## Ecosystem Management Handoff

The management handoff is:

```text
docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
```

That file defines:

```text
management_state
repo_state
source-of-truth files
automation chain
acceptance criteria
self-managed handoff completion
archive readiness
```

The management handoff is the repo-resident continuation source once this chat is archived.

## Publisher Closure Evidence Production

The current Publisher-side continuation packet is:

```text
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
python tools/check_publisher_closure_evidence_production.py
```

That packet defines the current evidence-production goal, required Publisher/Site artifact pair, freshness/order gate, pending-probe non-activation rule, pending-status boundary, and closure receipt condition.

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
tools/check_publisher_mirror_handoff.py
tools/check_mirror_ecosystem_management_handoff.py
tools/check_publisher_closure_evidence_production.py
```
