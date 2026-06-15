# Governance Receipts

## Purpose

This directory stores receipt stubs for Publisher governance cases.

A receipt stub is not the full evidence record. It is the compact transition record that preserves what kind of authority was claimed, what execution effect occurred, what access class was affected, and what admissibility posture currently applies.

## Relationship to Other Files

A full Publisher governance case may include:

```text
cases/<CASE-ID>.md
governance/cases/<CASE-ID>.case.json
governance/cases/<CASE-ID>.sources.json
governance/receipts/<CASE-ID>.receipt.json
```

The receipt file is the transition summary.

It should not replace the public case text, the source manifest, or the schema-compatible case object.

## Receipt Fields

A receipt stub should preserve at least:

```text
case_id
event_date
observed_date
authority_claim
execution_effect
affected_access_class
evidence_posture
disputed_claims
admissibility_status
publisher_path
source_manifest_path
receipt_path
```

## Boundary Rule

A public claim is not a receipt.

A news report is not a receipt.

A receipt records the current posture of the transition after available claims and sources have been separated.

## Current Receipt

```text
CASE-2026-06-ANTHROPIC-FABLE-MYTHOS-SUSPENSION.receipt.json
```

This receipt preserves the public posture of the reported Fable 5 / Mythos 5 access suspension as an unresolved emergency AI restriction case.

## Done State

A receipt is structurally ready when it identifies:

```text
the case it belongs to
the authority claim
the execution effect
the affected access class
the evidence posture
the disputed claims
the admissibility status
links back to the Publisher case and source manifest
```
