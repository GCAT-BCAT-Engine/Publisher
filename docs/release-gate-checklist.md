# Publisher to Site Release Gate Checklist

## Purpose

This checklist defines when a Publisher update may be treated as current on the StegVerse Site.

A green workflow alone is not the full release gate. The release gate requires source validity, dispatch validity, Site mirror validity, public-link verification, governance case posture preservation, Publisher receipt non-activation preservation, pending closure status preservation, and fresh ordered closure evidence.

## Scope

This checklist applies to Publisher updates that affect:

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
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/write_verification_run_receipt.py
tools/check_publisher_closure_evidence_production.py
```

## Gate 1 — Publisher Source Validity

Required before Site dispatch:

```text
Publisher source record exists
Publisher source record has intended status
case objects validate when case records changed
source manifests preserve evidence posture
receipts preserve transition posture
no draft/provisional/admissibility-limited record is strengthened by wording
```

Primary local activation command:

```bash
python tools/check_publisher_activation.py
```

The activation runner executes these underlying checks:

```bash
python tools/check_emergency_ai_templates.py
python tools/validate_emergency_ai_cases.py
python tools/check_site_mirror_dispatch.py
python tools/check_release_gate.py
python tools/check_verification_receipt_template.py
python tools/check_generate_papers_workflow.py
python tools/check_publisher_mirror_handoff.py
python tools/check_mirror_ecosystem_management_handoff.py
python tools/check_publisher_closure_evidence_production.py
```

## Gate 2 — Dispatch Readiness

Required before live dispatch:

```text
Publisher activation validation passes
SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher for live dispatch
Site target repository is StegVerse-Labs/Site unless intentionally testing
source_ref is main unless intentionally testing a branch or SHA
Publisher dispatch workflow resolves source_repository as GCAT-BCAT-Engine/Publisher
Publisher verification receipt artifact is produced only after a successful dispatch path
Publisher verification receipt preserves closure_evidence_results
Publisher verification receipt preserves closure_evidence_verification
Publisher verification receipt remains non-activating until a closure receipt is written
```

Dry run remains an optional diagnostic fallback, not the activation boundary.

## Gate 3 — Site Mirror Validity

Required after Site dispatch:

```text
Site mirror workflow starts
Site policy checker runs before mirroring
Site checks out Publisher at requested ref
Site finds _source/papers
Site regenerates papers/papers_manifest.json
Site regenerates Papers.html
Site regenerates papers/index.html
Site preserves alias redirects
Site workflow summary records source repository and source ref
Site evidence artifact is produced
```

## Gate 4 — Public Display Verification

Required before treating the Site display as current for this evidence window:

```text
Papers.html resolves
papers.html resolves or redirects
papers/index.html resolves
publisher/papers.html resolves or redirects
publisher/papers/index.html resolves or redirects
paper links resolve to mirrored Site paths
Site display does not overwrite Publisher status or posture
```

## Gate 5 — Governance Case Display Verification

Required when governance cases are displayed or linked:

```text
case_id is preserved
evidence posture is preserved
admissibility posture is preserved
source manifest remains separate from public narrative
receipt posture remains separate from public narrative
Site text does not convert disputed or provisional claims into final findings
```

## Gate 6 — Closure Evidence Verification

Required before marking activation complete:

```text
Publisher verification receipt artifact exists
Site evidence artifact exists
artifacts are fresh under MAX_ARTIFACT_AGE_HOURS
artifacts are ordered within ORDER_GRACE_MINUTES
Publisher pending closure status remains waiting_for_fresh_ordered_artifact_pair until closure
Publisher pending closure status is not an activation receipt
Publisher closure workflow runs tools/check_publisher_closure_evidence_production.py
Publisher closure workflow runs tools/close_site_mirror_activation.py
Publisher closure writes docs/mirror-activation-closures/<closure>.json
Publisher verification tracker is updated to activated
Publisher activation status is updated to activated
```

The pending probe is not an activation receipt.
Publisher verification receipts are not activation receipts.
The pending closure status is not an activation receipt.

## Release Decision

A Publisher to Site release is complete only when all applicable gates pass and the closure evidence gate writes an activation closure receipt.

If any gate fails, do not mark the Site display current. Fix the failing source, workflow, mirror, public-link, posture, artifact, freshness, ordering, receipt-boundary, pending-status, or closure condition and rerun from the earliest affected gate.

## Current Next Step

The next operational step is:

```text
Let the automated workflows proceed: Publisher dispatch produces a fresh Publisher receipt artifact, Site mirror produces a fresh Site evidence artifact, and Publisher closure workflow commits activation when both artifact classes are fresh, ordered, and evidence-valid.
```
