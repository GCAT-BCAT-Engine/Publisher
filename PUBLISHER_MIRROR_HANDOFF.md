# Publisher Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`.

## Current priority

```text
Goal: automatically ingest verified Ecosystem Chat activation evidence from StegVerse-Labs/Site and prepare bounded downstream publication status
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

The previous references to `StegVerse-Labs/stegguardian-wiki` and `StegVerse-Labs/Sit` were stale. The real Guardian destination is `StegVerse-002/stegguardian-wiki`; no `StegVerse-Labs/Sit` repository exists.

## Existing Standing-Proof Engine propagation

The earlier SPE v0.5.0 status remains recorded and is not superseded by this activation consumer. Its downstream wiki boundaries remain valid independently.

## Current blocker

```text
StegVerse-Labs/Site has not yet published ACTIVATION_COMPLETE with a hash-bound READY_FOR_DOWNSTREAM_INGESTION packet.
```

The Site scheduled workflow owns that transition after the adapter, deployment platform, and Master-Records custody service publish the required machine evidence.

## Next task

```text
1. Allow the hourly Publisher importer to observe Site activation automatically.
2. Preserve exact hash, binding, schema, destination, and authority-boundary rejection evidence.
3. Allow existing downstream wiki workflows to ingest Publisher status automatically.
4. Do not convert projection into publication authority, release authority, custody, or execution authority.
5. Tag or release only after repository validation and all required downstream evidence are complete.
```

## Authority boundary

```text
Site activation state != Publisher authority.
Propagation packet != publication authority.
Publisher import != release authority.
Publisher projection != custody.
Wiki projection != admissibility determination or Guardian enforcement authority.
Reconstruction PASS != execution authority.
No release tag is authorized by this handoff.
```

## Archive readiness

This handoff, the Site handoffs, Publisher importer, downstream consumer handoffs, workflows, projection records, and repository history preserve all continuation state. Earlier conversation context is not required and no manual user task remains.
