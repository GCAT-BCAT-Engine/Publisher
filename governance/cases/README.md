# Governance Cases

## Purpose

This directory stores machine-readable governance case support files used by Publisher.

Publisher is the republication surface. It can carry public-readable case studies, but case support files preserve source posture, validation posture, and receipt posture separately.

## File Types

A governed public case may have the following files:

```text
cases/<CASE-ID>.md
governance/cases/<CASE-ID>.case.json
governance/cases/<CASE-ID>.sources.json
governance/receipts/<CASE-ID>.receipt.json
```

## Meaning

```text
cases/<CASE-ID>.md
```

Public-readable Publisher case study.

```text
governance/cases/<CASE-ID>.case.json
```

Machine-readable case object that should validate against a schema.

```text
governance/cases/<CASE-ID>.sources.json
```

Source manifest. This separates public sources, screenshots, primary records, and missing records from the narrative case text.

```text
governance/receipts/<CASE-ID>.receipt.json
```

Receipt stub. This preserves the authority claim, execution effect, access class, evidence posture, and admissibility status.

## Emergency AI Restriction Cases

Emergency AI restriction case objects are validated against:

```text
governance/schemas/emergency-ai-restriction.case.schema.json
```

Run validation with:

```bash
python tools/validate_emergency_ai_cases.py
```

## Current Cases

```text
CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION
```

This case records the public dispute around the reported Fable 5 / Mythos 5 model access suspension under a U.S. export-control directive.

## Done State

A case is structurally ready when:

```text
public Markdown exists
case JSON exists
source manifest exists
receipt stub exists
case JSON validates against its schema
Publisher index links the case
```
