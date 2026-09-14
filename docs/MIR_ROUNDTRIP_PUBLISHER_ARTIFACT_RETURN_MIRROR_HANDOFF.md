# MIR round-trip Publisher artifact-return mirror handoff

Updated: 2026-09-14
Goal Task ID: `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`
COSV ID: `50000000100000`
Parent Site issue: `StegVerse-Labs/Site#1277`
SDK completion-capsule issue: `StegVerse-org/StegVerse-SDK#239`
SDK completion-capsule PR: `StegVerse-org/StegVerse-SDK#240`
SDK completion-capsule merge: `StegVerse-org/StegVerse-SDK@233632c35b0093166c16bdc660aa08e4ee1fe95a`
Publisher issue: `GCAT-BCAT-Engine/Publisher#70`
Publisher PR: `GCAT-BCAT-Engine/Publisher#71`
Publisher exact head validated: `598fc305103a710052d74c5389610ad1956cbd32`
Publisher artifact-return binding merge: `GCAT-BCAT-Engine/Publisher@40018e94a04e794e35dd499b4adc4296edb4b34c`
Status: `MERGED / PUBLISHER ARTIFACT-RETURN BINDING IMPLEMENTED VALIDATED MERGED / SDK RETURN AND EGRESS REMAIN`

## Purpose

Bind the SDK `stegverse.sdk.downstream-completion-capsule/v1` result into the existing Publisher exact-byte artifact-transfer/return path when the admitted manifest declares `completion.publisher.required = true`.

The Publisher stage produces or verifies exact canonical `stegverse.publisher.artifact-return/v1` bytes. It does not create a MIR-specific transport, scheduler, credential path, SDK return assembler, final egress surface, Interlock/InTr egress, far-side final transition, publication authority, release authority, execution authority, or authentic external MIR endpoint substitution.

## Implemented behavior

`publisher/intr_artifact_transfer.py` owns the canonical `stegverse.publisher.artifact-transfer/v1` to `stegverse.publisher.artifact-return/v1` path.

PR `#71` adds optional `roundtrip_binding` metadata on the exact transfer input. When present, the binding must satisfy:

- profile `stegverse.publisher.mir-roundtrip-binding/v1`;
- Goal Task ID `MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001`;
- COSV ID `50000000100000`;
- SDK completion capsule profile `stegverse.sdk.downstream-completion-capsule/v1`;
- `manifest_hash`, `completion_hash`, `response_to`, and `retained_packet_sha256` matching the SDK capsule;
- SDK state `SDK_MANIFEST_SELECTED_PROCESSING_EXECUTED` with `processor_result_observed = true`;
- Publisher requirement `completion.publisher.required = true`;
- Interlock/InTr egress and far-side transition still declared required;
- incoming `publisher_transition_observed = false` before Publisher produces the return;
- all later predicates false: SDK return binding, final StegVerse-side egress, Interlock/InTr egress, far-side transition, authentic MIR substitution, and communication completion;
- `authority_effect = NONE`.

After exact artifact rendering and artifact-manifest verification, the emitted return packet includes the same binding with only `publisher_transition_observed` promoted to true and with exact Publisher return identifiers appended:

- return schema;
- source export ID/hash;
- generation ID;
- artifact manifest SHA-256.

## Validation evidence

PR `#71` exact head `598fc305103a710052d74c5389610ad1956cbd32` was validated by:

```text
Architecture Guard #829: SUCCESS
Publisher Check #304: SUCCESS
Validate KV document pipeline #11: SUCCESS
Publisher Readiness #301: SUCCESS
Validate ERL KV Provider Proof Projection #7: SUCCESS
```

PR `#71` was squash-merged as `GCAT-BCAT-Engine/Publisher@40018e94a04e794e35dd499b4adc4296edb4b34c`.

`tests/test_intr_artifact_transfer.py` covers:

- existing exact transfer/render/return behavior;
- noncanonical transfer rejection;
- authority expansion rejection;
- MIR round-trip binding preservation in exact artifact return;
- fail-closed rejection when SDK capsule does not require Publisher;
- fail-closed rejection for completion-hash mismatch;
- fail-closed rejection when a returned packet attempts to promote SDK return binding.

## Current transition truth

```text
SDK admitted manifest/completion carry-forward: implemented, validated, and merged in StegVerse-SDK
Publisher exact artifact-transfer path: existing source path
Publisher MIR round-trip binding: implemented, validated, and merged in Publisher
Publisher artifact-return binding predicate: satisfied at source/build-test provenance by PR #71 merge
SDK return binding: not claimed
final StegVerse-side governed egress: not claimed
Interlock/InTr egress: not claimed
far-side final transition/caller receipt: not claimed
authentic external MIR endpoint substitution: not claimed
communication_complete: false
```

## Next after this merge

Continue to SDK return binding from exact Publisher return bytes. The next stage must consume canonical `stegverse.publisher.artifact-return/v1` bytes and bind them back to the original manifest/completion capsule without reconstructing equivalent Publisher output.
