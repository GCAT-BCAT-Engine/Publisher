# Governance Schemas

## Purpose

This directory stores JSON Schemas used to validate machine-readable Publisher governance case objects.

Schemas define structural admissibility for a case object. They do not decide whether the underlying public claim is true.

## Current Schemas

```text
emergency-ai-restriction.case.schema.json
```

This schema validates emergency AI restriction case objects, including cases involving model access suspension, export-control action, sovereign execution constraints, and frontier-model safety intervention.

## Validated Objects

Emergency AI case objects are stored as:

```text
governance/cases/*.case.json
```

They are validated by:

```text
tools/validate_emergency_ai_cases.py
```

and by the GitHub Actions workflow shown here without its leading dot:

```text
github/workflows/validate-emergency-ai-cases.yml
```

The actual repository path is `.github/workflows/validate-emergency-ai-cases.yml`.

## Boundary Rule

Schema validation means the case object has the required shape.

It does not mean:

```text
the government claim is true
the company claim is true
the exploit claim is verified
the source record is complete
the action is admissible
```

Schema validation only confirms that the object preserves enough structure for review.

## Schema Change Rule

Schema changes should be treated as governance changes.

Before changing an enum, required field, or validation rule, check whether existing case objects and receipts still match the intended posture.

## Local Validation

```bash
python -m pip install -r requirements.txt
python tools/validate_emergency_ai_cases.py
```
