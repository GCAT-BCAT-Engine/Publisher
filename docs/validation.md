# Validation

## Purpose

Publisher case records that use machine-readable JSON should validate before they are treated as ready for republication.

Publisher-to-Site activation also requires release-gate validation so documentation, workflow hooks, dispatch behavior, activation status, generated-paper workflow paths, verification receipt structure, handoff state, closure evidence production, and self-managed completion status do not drift from the operational boundary.

## Files

```text
governance/schemas/emergency-ai-restriction.case.schema.json
governance/cases/*.case.json
templates/emergency-ai-restriction.*
tools/validate_emergency_ai_cases.py
tools/check_emergency_ai_templates.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/check_verification_receipt_template.py
tools/check_generate_papers_workflow.py
tools/check_publisher_mirror_handoff.py
tools/check_mirror_ecosystem_management_handoff.py
tools/check_publisher_closure_evidence_production.py
tools/check_publisher_self_managed_completion.py
tools/check_publisher_activation.py
tools/create_emergency_ai_case_scaffold.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/verification-tracker.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/activation-status.md
docs/PUBLISHER_MIRROR_HANDOFF.md
docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md
docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md
docs/PUBLISHER_PENDING_CLOSURE_STATUS.md
docs/PUBLISHER_SELF_MANAGED_COMPLETION.md
github/workflows/generate-papers.yml
github/workflows/validate-emergency-ai-cases.yml
github/workflows/dispatch-site-mirror.yml
github/workflows/close-site-mirror-activation.yml
```

The workflow paths are shown without their leading dot. In the repository, they are stored under `.github/workflows/`.

## Create a New Emergency AI Case Scaffold

Generate the four-file case family from templates:

```bash
python tools/create_emergency_ai_case_scaffold.py CASE-YYYY-MM-SLUG \
  --title "Emergency AI Restriction Case Title" \
  --event-date EVENT-YYYY-MM-DD \
  --observed-date OBSERVED-YYYY-MM-DD
```

This creates:

```text
cases/CASE-YYYY-MM-SLUG.md
governance/cases/CASE-YYYY-MM-SLUG.case.json
governance/cases/CASE-YYYY-MM-SLUG.sources.json
governance/receipts/CASE-YYYY-MM-SLUG.receipt.json
```

Existing files are preserved by default. Use `--force` only when overwrite is intended.

## Local Validation

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the full activation validation sequence:

```bash
python tools/check_publisher_activation.py
```

That runner executes:

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
python tools/check_publisher_self_managed_completion.py
```

## Done State

Validation is passing when the full activation runner prints:

```text
valid: Publisher activation checks
```

The underlying checks should also print:

```text
valid: emergency AI templates
valid: Publisher Site mirror dispatch
valid: Publisher to Site release gate
valid: Publisher verification receipt template
valid: Generate Papers JSON workflow
valid: publisher mirror handoff
valid: mirror ecosystem management handoff
valid: publisher closure evidence production
valid: publisher self-managed completion
```

Self-managed completion means the repository contains the handoffs, workflows, validators, receipt boundary, pending-status runtime update, and closure updater needed to continue without prior chat context. It does not mean live activation has occurred.

Example case validation output:

```text
valid: governance/cases/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.case.json
```

All validation commands must exit with status code `0`.

## Failure State

Validation fails if:

```text
schema file is missing
no case JSON files are found
a case object does not match the schema
a template is missing
an ambiguous date placeholder is reintroduced
a scaffold output path is missing or inconsistent
Site mirror dispatch configuration drifts
release-gate documentation drifts
verification tracker drifts
iPhone dry-run instructions drift
verification receipt template drifts
Generate Papers JSON workflow paths drift
activation status drifts
Publisher mirror handoff drifts
ecosystem management handoff drifts
Publisher closure evidence production drifts
Publisher self-managed completion drifts
```

The validators print the relevant path or consistency error before exiting with status code `1`.
