# Validation

## Purpose

Publisher case records that use machine-readable JSON should validate before they are treated as ready for republication.

The current validators check case JSON structure and template scaffold consistency.

## Files

```text
governance/schemas/emergency-ai-restriction.case.schema.json
governance/cases/*.case.json
templates/emergency-ai-restriction.*
tools/validate_emergency_ai_cases.py
tools/check_emergency_ai_templates.py
tools/create_emergency_ai_case_scaffold.py
github/workflows/validate-emergency-ai-cases.yml
```

The workflow path is shown without its leading dot. In the repository, it is stored under `.github/workflows/validate-emergency-ai-cases.yml`.

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

## Done State

Validation is passing when the template checker prints:

```text
valid: emergency AI templates
```

and every emergency AI case object prints as valid while both commands exit with status code `0`.

Example:

```text
valid: governance/cases/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.case.json
```

## Failure State

Validation fails if:

```text
schema file is missing
no case JSON files are found
a case object does not match the schema
a template is missing
an ambiguous date placeholder is reintroduced
a scaffold output path is missing or inconsistent
```

The validators print the relevant path or consistency error before exiting with status code `1`.
