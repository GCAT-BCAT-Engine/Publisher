# Publisher Governed Ecosystem Workflow Runbook

## Purpose

This runbook defines how to verify Publisher governed ecosystem awareness without relying on prior chat context.

## Done condition

```text
validate-governed-ecosystem-awareness.yml completes successfully
```

## Workflow path

```text
github/workflows/validate-governed-ecosystem-awareness.yml
```

## Required checks

```text
Site mirror awareness check passes
StegGuardian propagation status check passes with destination pending
Publisher governed ecosystem sync status check passes
Publisher governed ecosystem validation status check passes
Publisher governed ecosystem workflow request check passes
```

## Evidence to record after green workflow

```text
workflow name
run date
commit SHA
result
remaining downstream destination status
```

## Boundary

A green workflow validates Publisher awareness only. It does not create production authority, release authorization, operational standing, live connector installation, canonical STRP admission, or downstream propagation.
