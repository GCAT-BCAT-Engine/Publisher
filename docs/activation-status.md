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
```

## What Is Not Yet Complete

```text
manual dry-run has not been recorded
SITE_MIRROR_DISPATCH_TOKEN has not been verified in Publisher
live Site dispatch has not been recorded
Site mirror workflow completion has not been recorded
public Site aliases have not been verified after live dispatch
release gate has not been marked passed
Site evidence packet has not been completed with live values
Site live evidence state has not been completed with live values
Publisher verification tracker has not been marked activated
```

## Activation Boundary

Repo activation occurs when:

```text
1. Dispatch Site Paper Mirror passes with dry_run: true.
2. Verification receipt is captured for the dry run.
3. Dispatch Site Paper Mirror passes with dry_run: false.
4. Site Mirror Papers from Publisher completes.
5. Site evidence packet is completed and validated.
6. Site live evidence state is completed and validated.
7. Verification receipt is captured for live dispatch.
8. docs/verification-tracker.md is updated from pending_dry_run to activated.
9. docs/activation-status.md is updated to activated.
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
Run Dispatch Site Paper Mirror manually with dry_run: true.
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
```

Note: workflow paths are displayed without the leading dot. The actual repository paths include the leading dot.
