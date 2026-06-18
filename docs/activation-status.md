# Publisher Activation Status

## Current State

```text
activation_state: ready_for_automated_push_dispatch
repository: GCAT-BCAT-Engine/Publisher
activation_target: Publisher to Site mirror dispatch
site_target: StegVerse-Labs/Site
```

## What Is Complete

```text
Publisher source validation exists
Emergency AI case validation exists
Site mirror dispatch workflow exists
Dispatch dry-run mode exists as optional diagnostic fallback
Site mirror dispatch checker exists
Release gate checklist exists
Release gate checker exists
Shared Publisher activation runner exists
Validation workflow uses the activation runner
Dispatch workflow uses the activation runner
Dispatch workflow runs on qualifying push to main
Dispatch workflow writes verification receipt artifacts automatically
Generate Papers JSON workflow exists
Generate Papers JSON workflow checker exists
Activation runner validates Generate Papers JSON workflow paths
Verification receipt template checker exists
Verification tracker exists
Verification tracker is aligned with automated dispatch evidence flow
iPhone dry-run runbook exists as fallback documentation
Verification run receipt template exists
Publisher mirror handoff exists
Publisher verification tracker is aligned with expanded mirror evidence sequence
Site mirror handoff exists
Site mirror evidence packet exists
Site live evidence state exists
```

## What Is Not Yet Complete

```text
automated Publisher dispatch run evidence has not been recorded in this status file
Publisher verification receipt artifact has not been recorded in this status file
dispatch credentials have not been confirmed by a successful dispatch run in this status file
live Site dispatch completion has not been recorded
live dispatch workflow URL has not been captured in this status file
Site mirror workflow completion has not been recorded
Site mirror workflow URL has not been captured in this status file
Site mirror commit SHA has not been captured in this status file
public Site aliases have not been verified after live dispatch
release gate has not been marked passed
Site evidence packet has not been completed with live values
Site live evidence state has not been completed with live values
Publisher verification tracker has not been marked activated
Publisher activation status has not been marked activated
```

## Activation Boundary

Repo activation occurs when:

```text
1. Publisher Generate Papers JSON completes for the intended source state.
2. Publisher Emergency AI validation completes.
3. python tools/check_publisher_activation.py returns valid: Publisher activation checks.
4. Qualifying push to main triggers Dispatch Site Paper Mirror.
5. Publisher workflow resolves Site repository and source ref.
6. Publisher workflow confirms dispatch credentials are configured without exposing credential values.
7. Publisher workflow dispatches Site mirror workflow.
8. Publisher workflow writes a verification receipt using tools/write_verification_run_receipt.py.
9. Publisher workflow uploads the verification receipt artifact.
10. Publisher live dispatch workflow URL is captured from workflow context or artifact metadata.
11. Site Mirror Papers from Publisher starts and completes.
12. Site mirror workflow URL is captured.
13. Site mirror commit SHA is captured.
14. Site manifest metadata is verified.
15. Public aliases are verified.
16. Site evidence packet is completed and validated.
17. Site live evidence state is completed and validated.
18. docs/verification-tracker.md is updated from pending_automated_dispatch to activated.
19. docs/activation-status.md is updated to activated.
```

## Current Validation Contract

Before dispatch completion, Publisher runs:

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

The Site mirror dispatch checker now also requires:

```text
tools/write_verification_run_receipt.py
publisher-site-verification-receipt artifact upload path
```

## Next Action

```text
Allow the push-triggered Dispatch Site Paper Mirror workflow to produce the Publisher verification receipt artifact, then use the artifact and Site workflow evidence to complete Site evidence files and final activation closure.
```

## Activation Evidence Files

```text
docs/verification-tracker.md
docs/verification-run-receipt.template.json
docs/release-gate-checklist.md
docs/validation.md
docs/PUBLISHER_MIRROR_HANDOFF.md
tools/check_publisher_activation.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
tools/write_verification_run_receipt.py
github/workflows/dispatch-site-mirror.yml
github/workflows/validate-emergency-ai-cases.yml
github/workflows/generate-papers.yml
StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
StegVerse-Labs/Site/docs/SITE_MIRROR_EVIDENCE_PACKET.md
StegVerse-Labs/Site/docs/SITE_MIRROR_LIVE_EVIDENCE_STATE.json
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.

## Archive Readiness

This activation status now contains the automated dispatch path, activation boundary, pending evidence list, and next action. Prior chat context is not required once this file, docs/verification-tracker.md, and docs/PUBLISHER_MIRROR_HANDOFF.md are present in the repository.
