# Publisher to Site Release Gate Checklist

## Purpose

This checklist defines when a Publisher update may be treated as current on the StegVerse Site.

A green workflow alone is not the full release gate. The release gate requires source validity, dispatch validity, Site mirror validity, and public-link verification.

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

Required commands:

```bash
python tools/check_emergency_ai_templates.py
python tools/validate_emergency_ai_cases.py
python tools/check_site_mirror_dispatch.py
```

## Gate 2 — Dispatch Readiness

Required before live dispatch:

```text
dry_run: true has passed
SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher for live dispatch
Site target repository is StegVerse-Labs/Site unless intentionally testing
source_ref is main unless intentionally testing a branch or SHA
Publisher dispatch workflow resolves source_repository as GCAT-BCAT-Engine/Publisher
```

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
```

## Gate 4 — Public Display Verification

Required before marking the Site display current:

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

## Release Decision

A Publisher to Site release is complete only when all gates pass.

If any gate fails, do not mark the Site display current. Fix the failing source, workflow, mirror, or public-link condition and rerun from the earliest affected gate.

## Current Next Step

The next operational step is:

```text
Run Dispatch Site Paper Mirror manually with dry_run: true.
```

If dry run passes, install or confirm `SITE_MIRROR_DISPATCH_TOKEN` and run a live dispatch.
