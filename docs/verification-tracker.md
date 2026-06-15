# Publisher to Site Verification Tracker

## Objective

Track the operational verification of the Publisher-to-Site mirror path after policy, dispatch, dry-run, and release-gate checks were added.

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
[ ] Run Dispatch Site Paper Mirror manually with dry_run: true.
[ ] Confirm Publisher validation passes.
[ ] Confirm tools/check_site_mirror_dispatch.py passes.
[ ] Confirm tools/check_release_gate.py passes.
[ ] Confirm workflow prints that Site mirror dispatch was not attempted.
[ ] Capture the dry-run result using docs/verification-run-receipt.template.json.
[ ] Install or confirm SITE_MIRROR_DISPATCH_TOKEN in Publisher.
[ ] Confirm Site can read Publisher for the mirror workflow.
[ ] Run Dispatch Site Paper Mirror manually with dry_run: false.
[ ] Confirm the Site Mirror Papers from Publisher workflow starts.
[ ] Confirm Site checks out GCAT-BCAT-Engine/Publisher at the intended ref.
[ ] Confirm Site policy checker runs before mirroring.
[ ] Confirm papers/papers_manifest.json, Papers.html, and papers/index.html update or are confirmed current.
[ ] Confirm workflow summary records source repository and source ref.
[ ] Confirm public aliases resolve or redirect.
[ ] Confirm governance case posture is not strengthened by Site wording.
[ ] Capture the live-dispatch result using docs/verification-run-receipt.template.json.
```

## Release Gate

Do not mark Site paper display current until every applicable check in `docs/release-gate-checklist.md` passes.

## Relevant Files

```text
.github/workflows/dispatch-site-mirror.yml
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/site-paper-display-policy.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
```

## Next Action

```text
Run Dispatch Site Paper Mirror manually with dry_run: true.
```
