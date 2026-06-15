# Governance

## Purpose

This directory contains the governance support layer for Publisher.

Publisher can present public-readable case studies, but the governance directory preserves the machine-readable structures that keep public narrative, source posture, receipt posture, and schema validation separate.

## Directory Map

```text
governance/cases/
governance/receipts/
governance/schemas/
```

## Layer Responsibilities

```text
governance/cases/
```

Stores machine-readable case objects and source manifests.

Case objects use the `*.case.json` suffix and should validate against a schema.

Source manifests use the `*.sources.json` suffix and preserve what is public, unverified, missing, or primary.

```text
governance/receipts/
```

Stores receipt stubs that summarize the transition posture of a case.

Receipts preserve authority claim, execution effect, affected access class, evidence posture, disputed claims, and admissibility status.

```text
governance/schemas/
```

Stores JSON Schemas used to validate machine-readable case objects.

Schema validation confirms structure. It does not prove truth, completeness, legality, or admissibility of the underlying event.

## Public Publisher Boundary

Public-readable case studies live outside this directory:

```text
cases/<CASE-ID>.md
```

Those files are the Publisher narrative surface.

The governance directory stores support records that allow that narrative to remain auditable and separable from evidence posture.

## Current Case Family

```text
CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION
```

This case family currently includes:

```text
cases/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.md
governance/cases/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.case.json
governance/cases/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.sources.json
governance/receipts/CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.receipt.json
```

## Validation

Emergency AI restriction cases are validated with:

```bash
python tools/validate_emergency_ai_cases.py
```

For more detail, see:

```text
docs/validation.md
governance/cases/README.md
governance/receipts/README.md
governance/schemas/README.md
```
