# Publisher Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`.

## Current priority

```text
Goal: automatically ingest verified Ecosystem Chat activation evidence from StegVerse-Labs/Site and prepare bounded downstream publication status
Parallel-safe goal: PUBLISHER-0001-DWD-PUBLICATION through pull/22
Result: AUTOMATED_SITE_ACTIVATION_IMPORT_AND_DOWNSTREAM_CONSUMERS_INSTALLED_SOURCE_ACTIVATION_PENDING
Manual user action required: false
```

## Source chain

```text
StegVerse-org/LLM-adapter retained activation state
-> master-records/orchestration retained custody state
-> StegVerse-Labs/Site authenticated imports and activation-state validation
-> StegVerse-Labs/Site/data/ecosystem-chat-activation-state.json
-> StegVerse-Labs/Site/data/ecosystem-chat-activation-propagation.json
-> GCAT-BCAT-Engine/Publisher automated importer
-> GCAT-BCAT-Engine/Publisher/data/ecosystem-chat-activation-status.json
-> automated downstream wiki consumers
```

## Installed consumer

```text
scripts/import_ecosystem_chat_activation.py
.github/workflows/import-ecosystem-chat-activation.yml
```

The workflow runs hourly and on dispatch. It fetches the public Site state and propagation packet, validates both canonical hashes, validates the packet-to-state hash binding, requires Publisher to be an explicit destination, and commits only changed projection state.

## Acceptance requirements

Publisher records `VERIFIED_ACTIVATION_IMPORTED` only when:

```text
Site state record type is correct
Site state_sha256 matches canonical state content
Site state = ACTIVATION_COMPLETE
all Site activation gates = true
propagation packet schema is correct
packet_sha256 matches canonical packet content
packet source_state_sha256 matches Site state_sha256
packet state = READY_FOR_DOWNSTREAM_INGESTION
Publisher destination exists
Publisher ingestion_ready = true
manual_user_action_required = false
all propagation authority-boundary flags = false
```

Missing or incomplete Site state remains `PENDING_SITE_ACTIVATION`. Invalid hashes, bindings, destinations, or authority fields become `REJECTED_SITE_ACTIVATION` and fail closed.

## Output

```text
data/ecosystem-chat-activation-status.json
```

The output is projection-only and always preserves:

```text
publication_authorized = false
release_authorized = false
custody_recorded = false
execution_authorized = false
manual_user_action_required = false
```

## Installed downstream consumers

```text
StegVerse-Labs/admissibility-wiki
  scripts/import_publisher_ecosystem_chat_activation.py
  scripts/generate_external_framework_page_status.py integration
  ECOSYSTEM_CHAT_ACTIVATION_HANDOFF.md

StegVerse-002/stegguardian-wiki
  scripts/import_publisher_ecosystem_chat_activation.py
  scripts/check_guardian_local_state.py integration
  ECOSYSTEM_CHAT_ACTIVATION_HANDOFF.md
```

Both consumers fetch Publisher's checked-in status automatically through their existing repository-owned workflows. Neither requires manual artifact download, file movement, workflow dispatch, route inspection, or user confirmation.

## Existing Standing-Proof-Engine continuity

Standing-Proof-Engine v0.5.0 status remains a separate continuity chain and is not superseded by Ecosystem Chat or Development Without Domination work.

Canonical source repository:

`StegVerse-Labs/Standing-Proof-Engine`

Canonical source handoff:

`SPE_MIRROR_HANDOFF.md`

Release snapshot:

`docs/release_snapshot_v0_5_0.md`

Source sample receipt:

`samples/destination_receipt_chain_001.json`

Master-Records destination:

`master-records/core-lite`

Master-Records receipt:

`records/spe_destination_receipt_chain_001.json`

Publisher status projection:

`data/spe-v0-5-0-status.json`

Wiki propagation verification remains independently required for `StegVerse-Labs/admissibility-wiki` and `StegVerse-002/stegguardian-wiki`. These references preserve validator continuity only; they do not assert that the current SPE chain is newly complete or activated.

## Development Without Domination parallel-safe owner

```text
task_id: PUBLISHER-0001-DWD-PUBLICATION
owner: pull/22
handoff: papers/development-without-domination/DEVELOPMENT_WITHOUT_DOMINATION_MIRROR_HANDOFF.md
machine_state: papers/development-without-domination/publication-status.json
validator: tools/check_development_without_domination_publication.py
state: VALIDATOR_AND_MACHINE_STATE_INSTALLED
publication_authority: false
release_authority: false
```

The exact PDF and DOCX remain absent from Publisher custody. Site exact-byte transport is separately owned by `StegVerse-Labs/Site#142`. Publisher must remain fail-closed until local artifacts and the verified Site route receipt exist.

## Autonomous adjacent-construction ownership

Publisher owns the no-manual-action bootstrap for the StegPay/StegOps two-generation construction goal.

Installed files:

```text
scripts/autonomous_adjacent_construction_bootstrap.py
.github/workflows/autonomous-adjacent-construction-bootstrap.yml
```

Repository-owned behavior:

1. fetch and validate the authoritative StegOps construction plan;
2. require this handoff marker before accepting Publisher as target one;
3. generate and self-validate the Publisher packet and Publisher-owned completion receipt;
4. preserve all publication, release, custody, deployment, payment, entitlement, and execution authority flags as false;
5. install only the bounded Site intake paths declared by the plan;
6. dispatch Site only after Publisher receipt validation;
7. require Site to persist its own receipt;
8. allow StegOps to pull both receipts and close only on `TWO-GENERATION AUTONOMY: COMPLETE`.

## Current blockers

```text
Ecosystem Chat: StegVerse-Labs/Site has not published ACTIVATION_COMPLETE with a hash-bound READY_FOR_DOWNSTREAM_INGESTION packet.
Development Without Domination: exact Publisher artifacts and verified Site publication receipt are absent.
```

Every blocker has a repository-native observer and machine-readable release condition. No unspecified external task exists.

## Next tasks

```text
1. Observe and repair pull/22 workflow evidence.
2. Continue exact Site artifact transport under StegVerse-Labs/Site#142.
3. Install Publisher exact artifacts and validate their hashes.
4. Consume the verified Site publication receipt.
5. Preserve exact hash, binding, schema, destination, sequence, and authority-boundary rejection evidence.
6. Do not convert projection or transport into publication, release, custody, deployment, payment, entitlement, or execution authority.
```

## Authority boundary

```text
Site activation state != Publisher authority.
Propagation packet != publication authority.
Publisher import != release authority.
Publisher projection != custody.
Adjacent-construction transport != target acceptance.
Publisher receipt != Site receipt.
Wiki projection != admissibility determination or Guardian enforcement authority.
Reconstruction PASS != execution authority.
No release tag is authorized by this handoff.
```

## Archive readiness

Archive is prohibited while pull/22, Site pull/142, exact artifact custody, Site route verification, Publisher receipt validation, or downstream propagation remains incomplete. Repository state contains the continuation path, but active work remains.
