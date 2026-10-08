# Economic paper SDK manifest — Publisher native source consumer

Existing Goal: `ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001`.

`publisher/economic_paper_manifest_consumer.py` is the Publisher-native source consumer for the exact manifest produced by the merged SDK `publisher_paper_publication.py`. It independently checks the exact paper bytes, SHA-256 and Git blob, Publisher `papers/` target, owner approval, supplied economics/legal report digest references, governance candidate, non-authorizing posture request, Publisher stage and Interlock/InTr egress.

The output `SOURCE_BOUND_MANIFEST_ACCEPTED` is not an InTr decision, Master Records receipt, publication authorization, release authorization or repository mutation. It exists so Publisher can reject a malformed or wrong-target SDK manifest before any consequential path. The next runtime binding remains the existing SDK universal manifest state-transition runtime. TV/TVC remains credential authority, Interlock/InTr transition authority and Master Records organization records and reconstruction.

This source consumer does not create a second runtime and does not require a resident device or hosted worker. Organization-ledger history must be read from an authorized sovereign organization ledger interface when available. The existing resident-local readback implementation is not made a prerequisite for this economic task; its own source contract forbids hosted execution and requires a private resident runtime. If no authenticated organization-ledger interface is reachable from the active authorized execution surface, historical runtime evidence remains `UNKNOWN_NOT_AUTHENTICALLY_OBSERVED`, not a fabricated DENY.

The currently inspected Publisher review packet does not contain attributable original banker/lawyer report bytes. A caller cannot substitute arbitrary 64-hex values for real review evidence merely to obtain source admission; applicability and authenticity remain Publisher policy/evidence questions upstream of the actual manifest attempt.
