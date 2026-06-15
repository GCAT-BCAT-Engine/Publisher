# Validation

## Purpose

Publisher case records that use machine-readable JSON should validate before they are treated as ready for republication.

Publisher-to-Site activation also requires release-gate validation so documentation, workflow hooks, dry-run instructions, activation status, and verification receipt structure do not drift from the operational boundary.

## Files

```text
governance/schemas/emergency-ai-restriction.case.schema.json
governance/cases/*.case.json
templates/emergency-ai-restriction.*
tools/validate_emergency_ai_cases.py
tools/check_emergency_ai_templates.py
tools/check_site_mirror_dispatch.py
tools/check_release_gate.py
tools/create_emergency_ai_case_scaffold.py
docs/site-mirror-dispatch-protocol.md
docs/release-gate-checklist.md
docs/verification-tracker.md
docs/iphone-dry-run-runbook.md
docs/verification-run-receipt.template.json
docs/activation-status.md
github/workflows/validate-emergency-ai-cases.yml
github/workflows/dispatch-site-mirror.yml
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

Check template consistency:

```bash
python tools/check_emergency_ai_templates.py
```

Run case object validation:

```bash
python tools/validate_emergency_ai_cases.py
```

Check Publisher-to-Site mirror dispatch configuration:

```bash
python tools/check_site_mirror_dispatch.py
```

Check release-gate and activation boundary integrity:

```bash
python tools/check_release_gate.py
```

## Done State

Validation is passing when the template checker prints:

```text
valid: emergency AI templates
```

and every emergency AI case object prints as valid while the dispatch checker and release-gate checker also print:

```text
valid: Publisher Site mirror dispatch
valid: Publisher to Site release gate
```

Example:

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
activation status drifts
```

The validators print the relevant path or consistency error before exiting with status code `1`.
