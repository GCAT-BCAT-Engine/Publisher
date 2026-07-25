# Publisher Activation Orchestration Repair

## Canonical progression

```text
Site activation state
+ Site propagation packet
+ Master-Records custody of the Site terminal orchestration receipt
-> Publisher validation
-> bounded Publisher projection
-> downstream consumer validation
```

## Required evidence

Publisher must not record `VERIFIED_ACTIVATION_IMPORTED` unless all three inputs are present, hash-valid, and mutually bound:

1. `ecosystem-chat-activation-state.json` reports `ACTIVATION_COMPLETE` and every activation gate is true.
2. `ecosystem-chat-activation-propagation.json` reports `READY_FOR_DOWNSTREAM_INGESTION`, names Publisher as an ingestion-ready destination, and binds the Site state hash.
3. `site-orchestration-terminal-custody.json` reports Master-Records custody `RECORDED`, reconstruction `PASS`, exact commit binding, complete stage-chain reconstruction, and clear supersession state.

The Site state and propagation packet must both bind the same `terminal_custody_sha256` recorded by the custody projection.

## Trigger repair

The previous hourly importer and `cancel-in-progress: false` behavior were removed. The canonical importer now runs only on explicit dispatch or bounded changes to its own orchestration contract on `main`. Superseded runs are cancelled. Manual dispatch is validation-only. Persistent projection mutation is restricted to a `main` push run and machine-owned commits use `[skip ci]`.

## Authority boundary

```text
Site activation != Publisher authority
terminal custody != publication authority
Publisher projection != custody
workflow completion != release authority
transport != admissibility
```

## Remaining live evidence

The implementation remains fail-closed until Site publishes a real hash-bound terminal custody projection generated from a completed Site workflow and reconstructed by `master-records/orchestration`. Downstream consumers must reject Publisher status unless the Publisher record itself preserves the terminal custody hash and reports `terminal_custody_verified = true`.
