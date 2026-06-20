# Site Mirror Dispatch Protocol

## Purpose

This protocol defines how Publisher should notify `StegVerse-Labs/Site` that current paper or case-study display data may need to be refreshed.

Publisher remains the source of truth. Site remains the public display surface.

## Publisher Dispatch Workflow

The Publisher workflow that performs validation and dispatch is:

```text
.github/workflows/dispatch-site-mirror.yml
```

The workflow name is:

```text
Dispatch Site Paper Mirror
```

It runs after eligible Publisher changes on `main` and may also be run manually.

The dispatch workflow uses the shared activation runner before any dry-run completion or live Site dispatch:

```bash
python tools/check_publisher_activation.py
```

The activation runner executes the emergency-template check, emergency-case validation, Site mirror dispatch configuration check, Publisher-to-Site release-gate check, verification receipt template check, Generate Papers workflow check, Publisher mirror handoff check, ecosystem management handoff check, and Publisher closure evidence production check.

## Closure Evidence Guard

The dispatch path is now bound to the Publisher closure evidence production packet and the pending closure status:

```text
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
tools/check_publisher_closure_evidence_production.py
```

This prevents the dispatch path from treating activation as complete unless the closure path remains capable of rejecting missing, stale, out-of-order, or evidence-incomplete Publisher/Site artifact pairs.

The pending closure status must remain non-activating until fresh ordered artifacts are observed:

```text
publisher_receipt_recorded_here: false
site_evidence_recorded_here: false
closure_recorded_here: false
pending_probe_only: true
```

Publisher dispatch receipts must also preserve the closure-evidence boundary:

```text
CLOSURE_EVIDENCE_STATUS: pending_fresh_ordered_artifacts
CLOSURE_EVIDENCE_VERIFICATION: pending_fresh_ordered_artifacts
MAX_ARTIFACT_AGE_HOURS: 48
ORDER_GRACE_MINUTES: 5
PENDING_PROBE_PATH: docs/mirror-activation-closures/publisher-site-mirror-pending.json
```

Those values describe dispatch receipt posture only. They do not activate the mirror.

## Target Site Workflow

The target Site workflow is:

```text
StegVerse-Labs/Site/.github/workflows/mirror-papers.yml
```

The workflow name is:

```text
Mirror Papers from Publisher
```

The workflow accepts these dispatch inputs:

```text
source_repository
source_ref
```

Default values should be:

```text
source_repository: GCAT-BCAT-Engine/Publisher
source_ref: main
```

## Dispatch Eligibility

Publisher may dispatch the Site mirror workflow after changes to:

```text
papers/**
papers_manifest.yml
papers.json
cases/**
governance/cases/**
governance/receipts/**
docs/site-paper-display-policy.md
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/validation.md
docs/verification-tracker.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
tools/check_publisher_activation.py
tools/check_publisher_mirror_handoff.py
tools/check_mirror_ecosystem_management_handoff.py
tools/check_publisher_closure_evidence_production.py
```

Publisher should not dispatch Site if Publisher activation validation fails.

## Required Dispatch Sequence

Use this order:

```text
1. Publisher paper or case source record changes.
2. Publisher activation validation passes.
3. Publisher sends workflow_dispatch to Site mirror workflow.
4. Site mirror workflow runs Site policy checker.
5. Site checks out Publisher at the requested ref.
6. Site mirrors papers and regenerates indexes.
7. Site writes and uploads the Site evidence artifact.
8. Publisher closure workflow observes Publisher and Site artifacts.
9. Publisher closure workflow writes a pending probe or activation closure receipt.
```

## Required Token Boundary

The dispatch credential must be limited to the minimum access required to trigger the Site workflow.

The Site mirror workflow separately needs read access to Publisher if Publisher is private or otherwise inaccessible to the default workflow token.

Suggested secret names:

```text
SITE_MIRROR_DISPATCH_TOKEN
STEGVERSE_REPO_SYNC_TOKEN
```

`SITE_MIRROR_DISPATCH_TOKEN` belongs in Publisher when Publisher dispatches Site.

`STEGVERSE_REPO_SYNC_TOKEN` belongs in Site when Site must read Publisher.

## Dry-Run Procedure

Use dry run before installing or relying on cross-repo dispatch credentials.

```text
1. Open GCAT-BCAT-Engine/Publisher Actions.
2. Select Dispatch Site Paper Mirror.
3. Run workflow on main.
4. Set dry_run to true.
5. Leave site_repository as StegVerse-Labs/Site unless testing a fork.
6. Leave source_ref as main unless testing a branch or SHA.
7. Confirm Publisher activation validation passes.
8. Confirm the workflow prints that Site mirror dispatch was not attempted.
```

Dry run does not require `SITE_MIRROR_DISPATCH_TOKEN` and does not trigger the Site workflow.

## Manual Dispatch Procedure

To test live dispatch after dry run passes:

```text
1. Confirm SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher.
2. Open GCAT-BCAT-Engine/Publisher Actions.
3. Select Dispatch Site Paper Mirror.
4. Run workflow on main.
5. Set dry_run to false.
6. Leave site_repository as StegVerse-Labs/Site unless testing a fork.
7. Leave source_ref as main unless testing a branch or SHA.
8. Confirm Publisher activation validation passes.
9. Confirm the Site workflow starts.
10. Confirm Site mirror completes and records the source repository and ref.
11. Confirm Publisher closure writes a pending probe or activation closure receipt.
```

## Failure Handling

If dispatch fails, Publisher should not mark the Site display as current.

If Site mirror fails, Site should keep the last successful public display and expose failure through workflow logs rather than silently publishing partial mirror output.

If closure evidence is missing, stale, out-of-order, or evidence-incomplete, Publisher should write or retain a pending probe and must not mark activation complete.

## Done State

Publisher-to-Site dispatch is complete when:

```text
Publisher activation validation passes
Publisher dry run passes without requiring a dispatch token
Publisher can trigger Site mirror workflow
Site policy checker runs before mirroring
Site records source repository and source ref in workflow summary
Site commit references Publisher as source
Site evidence artifact is produced
Publisher closure writes a pending probe or activation closure receipt
```
