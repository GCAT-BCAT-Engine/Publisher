# Publisher Activation Status

## Current State

```text
activation_state: ready_for_manual_dry_run
repository: GCAT-BCAT-Engine/Publisher
activation_target: Publisher to Site mirror dispatch
site_target: StegVerse-Labs/Site
```

## What Is Complete

```text
Publisher source validation exists
Emergency AI case validation exists
Site mirror dispatch workflow exists
Dispatch dry-run mode exists
Site mirror dispatch checker exists
Release gate checklist exists
Release gate checker exists
Shared Publisher activation runner exists
Validation workflow uses the activation runner
Dispatch workflow uses the activation runner
Generate Papers JSON workflow exists
Generate Papers JSON workflow checker exists
Activation runner validates Generate Papers JSON workflow paths
Verification receipt template checker exists
Verification tracker exists
iPhone dry-run runbook exists
Verification run receipt template exists
Publisher mirror handoff exists
Publisher verification tracker is aligned with expanded mirror evidence sequence
Site mirror handoff exists
Site mirror evidence packet exists
```

## What Is Not Yet Complete

```text
manual dry-run has not been recorded
dry-run workflow URL has not been captured
dry-run receipt commit has not been captured
dispatch credentials have not been confirmed in this status file
live Site dispatch has not been recorded
live dispatch workflow URL has not been captured
Site mirror workflow completion has not been recorded
Site mirror workflow URL has not been captured
Site mirror commit SHA has not been captured
public Site aliases have not been verified after live dispatch
release gate has not been marked passed
Site evidence packet has not been completed with live values
Site live evidence state has not been completed with live values
live-dispatch receipt commit has not been captured
Publisher verification tracker has not been marked activated
Publisher activation status has not been marked activated
```

## Activation Boundary

Repo activation occurs when:

```text
1. Publisher Generate Papers JSON completes for the intended source state.
2. Publisher Emergency AI validation completes.
3. python tools/check_publisher_activation.py returns valid: Publisher activation checks.
4. Dispatch Site Paper Mirror passes with dry_run: true.
5. Dry-run workflow URL is captured.
6. Verification receipt is captured and committed for the dry run.
7. Dispatch credentials are confirmed configured without exposing credential values.
8. Dispatch Site Paper Mirror passes with dry_run: false.
9. Publisher live dispatch workflow URL is captured.
10. Site Mirror Papers from Publisher starts and completes.
11. Site mirror workflow URL is captured.
12. Site mirror commit SHA is captured.
13. Site manifest metadata is verified.
14. Public aliases are verified.
15. Site evidence packet is completed and validated.
16. Site live evidence state is completed and validated.
17. Verification receipt is captured and committed for live dispatch.
18. docs/verification-tracker.md is updated from pending_dry_run to activated.
19. docs/activation-status.md is updated to activated.
```

## Current Validation Contract

Before dry-run completion or live dispatch, Publisher runs:

```text
python tools/check_publisher_activation.py
```

That activation runner currently includes:

```text
tools/check_emergency_ai_templates.py
tools/validate_emergency_ai_cases.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
```

## Next Action

```text
Run Dispatch Site Paper Mirror manually with dry_run: true, then capture the dry-run workflow URL and dry-run receipt commit before live dispatch.
```

## Activation Evidence Files

```text
docs/verification-tracker.md
docs/verification-run-receipt.template.json
docs/release-gate-checklist.md
docs/iphone-dry-run-runbook.md
docs/validation.md
docs/PUBLISHER_MIRROR_HANDOFF.md
tools/check_publisher_activation.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
github/workflows/dispatch-site-mirror.yml
github/workflows/validate-emergency-ai-cases.yml
github/workflows/generate-papers.yml
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.

## Archive Readiness

This activation status now contains the current activation boundary, pending evidence list, and next action. Prior chat context is not required once this file, docs/verification-tracker.md, and docs/PUBLISHER_MIRROR_HANDOFF.md are present in the repository.
