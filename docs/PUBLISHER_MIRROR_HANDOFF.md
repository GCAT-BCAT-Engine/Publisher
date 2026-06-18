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
Activation state: ready_for_manual_dry_run
```

## Built Files

```text
.github/workflows/dispatch-site-mirror.yml
.github/workflows/validate-emergency-ai-cases.yml
tools/check_publisher_activation.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
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

## Publisher Mirror Contract

Publisher remains the source of truth. Site remains the public display surface.

Publisher may dispatch Site only after Publisher activation validation passes.

The Publisher dispatch workflow is displayed as:

```text
github/workflows/dispatch-site-mirror.yml
```

The actual repository path includes the leading dot.

The target Site workflow is displayed as:

```text
StegVerse-Labs/Site/github/workflows/mirror-papers.yml
```

The actual Site repository path includes the leading dot.

## Required Validation Command

Before dry-run completion or live dispatch, Publisher runs:

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
```

## Required Run Order

```text
1. Publisher: Run Dispatch Site Paper Mirror manually with dry_run: true.
2. Publisher: Confirm activation validation completes.
3. Publisher: Confirm tools/check_publisher_activation.py prints valid: Publisher activation checks.
4. Publisher: Confirm dry run prints that Site mirror dispatch was not attempted.
5. Publisher: Capture dry-run receipt using docs/verification-run-receipt.template.json.
6. Publisher: Install or confirm SITE_MIRROR_DISPATCH_TOKEN.
7. Site: Confirm Site can read Publisher for mirror workflow.
8. Publisher: Run Dispatch Site Paper Mirror manually with dry_run: false.
9. Site: Confirm Mirror Papers from Publisher workflow starts.
10. Site: Confirm papers/papers_manifest.json includes source metadata.
11. Site: Confirm public aliases resolve.
12. Publisher: Capture live-dispatch receipt.
13. Publisher: Update docs/verification-tracker.md from pending_dry_run to activated.
14. Publisher: Update docs/activation-status.md to activated after evidence is recorded.
```

## Evidence To Capture

```text
Publisher dry-run workflow URL
Publisher dry-run receipt commit
Publisher live dispatch workflow URL
Site mirror workflow URL
Site mirror commit SHA
papers/papers_manifest.json source_repository
papers/papers_manifest.json source_ref
papers/papers_manifest.json source_of_truth
public alias verification results
Publisher live-dispatch receipt commit
Publisher verification tracker activation commit
Publisher activation-status update commit
```

## Current Delta

```text
Resolved: Publisher validation, release gate, dispatch protocol, dry-run mode, receipt template, and verification tracker exist.
Resolved: Site checked-in papers/papers_manifest.json now includes required source metadata.
Pending: Publisher manual dry run, Publisher live dispatch, Site workflow evidence, alias verification, receipt commits, verification tracker activation, and activation-status update.
```

## Companion Site Handoff

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
```

## Archive Readiness

This handoff contains the Publisher repo state, next run order, and evidence requirements needed to continue. Prior chat thread context is not required for forward progress once this file is present in the repository.
