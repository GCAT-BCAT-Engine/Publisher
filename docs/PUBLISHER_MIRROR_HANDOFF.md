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
1. Publisher: Generate Papers JSON.
2. Publisher: Validate Emergency AI Cases.
3. Publisher: run python tools/check_publisher_activation.py.
4. Publisher: confirm tools/check_publisher_activation.py prints valid: Publisher activation checks.
5. Publisher: run Dispatch Site Paper Mirror manually with dry_run: true.
6. Publisher: confirm dry run prints that Site mirror dispatch was not attempted.
7. Publisher: capture dry-run workflow URL.
8. Publisher: capture dry-run receipt commit using docs/verification-run-receipt.template.json.
9. Publisher: confirm dispatch credentials are configured.
10. Publisher: run Dispatch Site Paper Mirror manually with dry_run: false.
11. Publisher: capture live dispatch workflow URL.
12. Site: confirm Mirror Papers from Publisher workflow starts and completes.
13. Site: capture Site mirror workflow URL.
14. Site: capture Site mirror commit SHA.
15. Site: confirm papers/papers_manifest.json includes source metadata.
16. Site: confirm public aliases resolve.
17. Site: update docs/SITE_MIRROR_EVIDENCE_PACKET.md with real evidence values.
18. Site: run python scripts/check_site_mirror_evidence_packet.py.
19. Publisher: capture live-dispatch receipt commit.
20. Publisher: update docs/verification-tracker.md from pending_dry_run to activated.
21. Publisher: update docs/activation-status.md to activated after evidence is recorded.
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
Resolved: Publisher handoff run order now separates validation, dry-run workflow capture, dry-run receipt commit, dispatch credential confirmation, live dispatch, Site evidence capture, Site evidence-packet validation, live-dispatch receipt commit, verification tracker activation, and activation-status update.
Pending: Publisher manual dry run, dry-run receipt commit, Publisher live dispatch, Site workflow evidence, alias verification, Site evidence packet completion, live-dispatch receipt commit, verification tracker activation, and activation-status update.
```

## Companion Site Handoff

```text
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
```

## Archive Readiness

This handoff contains the Publisher repo state, next run order, and evidence requirements needed to continue. Prior chat thread context is not required for forward progress once this file is present in the repository.
