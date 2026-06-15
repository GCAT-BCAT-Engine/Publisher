# Templates

## Purpose

This directory stores reusable templates for Publisher governance records.

Templates are not case records. They are starting points for creating structurally consistent public case drafts, case objects, source manifests, and receipts.

## Current Templates

```text
templates/emergency-ai-restriction.public-case.template.md
templates/emergency-ai-restriction.case.template.json
templates/emergency-ai-restriction.sources.template.json
templates/emergency-ai-restriction.receipt.template.json
```

## Emergency AI Restriction Template Set

```text
templates/emergency-ai-restriction.public-case.template.md
```

Use this to start the public-readable Publisher case study.

Copy it into:

```text
cases/<CASE-ID>.md
```

```text
templates/emergency-ai-restriction.case.template.json
```

Use this to start the schema-compatible machine-readable case object.

Copy it into:

```text
governance/cases/<CASE-ID>.case.json
```

```text
templates/emergency-ai-restriction.sources.template.json
```

Use this to start the source manifest.

Copy it into:

```text
governance/cases/<CASE-ID>.sources.json
```

```text
templates/emergency-ai-restriction.receipt.template.json
```

Use this to start the receipt stub.

Copy it into:

```text
governance/receipts/<CASE-ID>.receipt.json
```

## Placeholder Replacement

Replace all placeholder values before treating a generated file as case-ready, including:

```text
CASE-YYYY-MM-SLUG
YYYY-MM-DD
Emergency AI Restriction Case Title
https://example.com/source
LOCAL-FILE-OR-IMAGE-ID
```

## Validation

After creating a case object, run:

```bash
python tools/validate_emergency_ai_cases.py
```

The case object should not be treated as structurally ready until it validates against:

```text
governance/schemas/emergency-ai-restriction.case.schema.json
```

## Boundary Rule

A template does not establish evidence.

A template does not create authority.

A template does not create a receipt until populated with case-specific transition posture.

A template does not create a public case until populated with case-specific public narrative and boundary language.

A template only preserves structure so the resulting case can separate:

```text
public narrative
source posture
receipt posture
schema posture
admissibility posture
```
