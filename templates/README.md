# Templates

## Purpose

This directory stores reusable templates for Publisher governance records.

Templates are not case records. They are starting points for creating structurally consistent case objects, source manifests, receipts, and public case drafts.

## Current Templates

```text
templates/emergency-ai-restriction.case.template.json
```

This template is used to start a new emergency AI restriction case object.

## Use

Copy the template into:

```text
governance/cases/<CASE-ID>.case.json
```

Then replace all placeholder values, including:

```text
CASE-YYYY-MM-SLUG
YYYY-MM-DD
Emergency AI Restriction Case Title
https://example.com/source
```

## Validation

After creating a case object, run:

```bash
python tools/validate_emergency_ai_cases.py
```

The case should not be treated as structurally ready until it validates against:

```text
governance/schemas/emergency-ai-restriction.case.schema.json
```

## Boundary Rule

A template does not establish evidence.

A template does not create authority.

A template only preserves structure so the resulting case can separate:

```text
public narrative
source posture
receipt posture
schema posture
admissibility posture
```
