# SDK reviewer-facing Publisher evidence: generic source package + exact originals

Owner: existing Publisher document pipeline, InTr artifact transfer/return, MIR round-trip issue #70 (specialized binding unchanged).
Consumer: canonical `MIR-SV-CAPABILITY-BOUNDARY-EXPERIMENT-003`, StegVerse-Labs/.github issue #2682, COSV `50000000100000`.

## Why

For a review-facing SDK manifest, `completion.publisher.required` should default to true while non-review SDK runs remain allowed to omit Publisher. This existing Publisher adapter handles the document/report stage; it is *not* a new runtime, scheduling service, governance or Master Records custody plane.

The historical MIR round-trip binding profile stays fixed to its existing MIR-CONNECTION-ROUNDTRIP-TECHNICAL-GUIDE-001 owner. A different experiment **must not reuse that owner ID** merely because its COSV happens to match. The generic `stegverse.publisher.artifact-transfer/v1` packet without that specific binding remains compatible with SDK's generic return assembler; it does not assert original SDK completion-capsule lineage without an authentic binding. Matching actual SDK manifests to returned packages requires the existing authenticated transport/custody readback. The generic return path cannot manufacture that runtime proof.

## Existing adapter extended in place

- Publisher `publisher/intr_artifact_transfer.py` accepts optional `evaluator_assets` on its existing exact canonical transfer envelope; each attachment includes safe `evidence/...name.ext` path, MIME, original SHA-256, byte count, base64 content and attributed source class.
- The existing `publisher/document_pipeline.py` accepts the explicitly distinct `stegverse.publisher.evidence-report-package/v1` export source class **without pretending that a GitHub/SDK reviewer package originated in the user's private KV**. The KV contract remains unchanged.
- Each exact original is retained byte-identically inside the existing returned Publisher artifact bundle and is listed and hashed in the *same* artifact manifest and rendering receipt as the document's output formats. Output files and returned payload can independently verify every digest. Original evidence can be individually reviewed, not merely inferred from a checksum list.
- A generic report whose evidence inventory declares an exact `evidence/` original must supply its matching bytes in `evaluator_assets`; missing originals, path traversal, duplicate names, wrong MIME, altered bytes, changed manifest/receipt hashes or publication/release authority expansion fail closed.
- The report's authorship/source/claim and observer status remain differentiated. These exact-byte checks **do not** authenticate a screenshot's LinkedIn account, prove physical activity, create a Master Records receipt or prove the existence of a sovereign resident Publisher transition.
- The existing optional specialized MIR `roundtrip_binding` remains supported, separately validated and unchanged. `evaluator_assets` may accompany it when the original owner has its authentic SDK downstream capsule.

## Activation and limit

The generic report fixture is source-only. A real review run needs: authorized SDK result and retained evidence through existing InTr, an exact canonical generic report transfer, Publisher output/receipt observed at its *actual* destination, original byte readback, SDK exact return binding and downstream InTr/far-side receipts. Local unit tests do **not** claim any of those runtime transitions.

For Experiment 3 the original user-supplied MIR PDF and ten screenshots are retained in the conversation archive; their hashes are in the central canonical handoff. They are **not** re-encoded as fictitious fixtures or silently uploaded to this public repository. The exact original archive and source-labeled evaluator report can be delivered as a separate complete reviewer package without exposing unrelated user data.
