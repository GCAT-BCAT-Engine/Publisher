# Source Geometry Provenance Note

## Purpose

This note records how the Publisher repository should reference the original hand-drawn source geometry now documented by the Admissibility Wiki as SG-001.

Publisher is a paper and public-record publishing surface. It may cite or mirror source-geometry provenance when relevant to a paper, case study, or formalism chronology, but it is not the authority for that provenance record.

## Current Source of Truth

```yaml
source_geometry_provenance:
  source_repository: StegVerse-Labs/admissibility-wiki
  source_page: docs/formalisms/original-drawing-reference.md
  public_page: https://stegverse-labs.github.io/admissibility-wiki/docs/formalisms/original-drawing-reference
  source_geometry_id: SG-001
  creator: Rigel Randolph
  artifact_classification: pre_BCAT_GCAT_recoverability_geometry
  current_earliest_preserved_copy: "2026-03-05"
  earlier_upload_state: not_yet_located
  publisher_role: citation_and_publication_surface_only
```

## Relationship to BCAT/GCAT

The original drawing is recorded as a pre-BCAT/GCAT recoverability geometry.

The currently preserved evidence indicates that photographs of the hand-drawn paper artifact exist dated 2026-03-05. Those preserved photographs predate the later BCAT/GCAT formalization work and may be relevant to formalism chronology.

This repository should use the careful classification:

```text
pre-BCAT/GCAT precursor source geometry
```

It should not use stronger claims such as:

```text
proof of BCAT/GCAT derivation
proof of priority
proof of admissibility
proof of formal correctness
```

unless a separate reviewed paper, provenance packet, or proof artifact establishes that stronger claim.

## Publisher Citation Rule

When a Publisher paper, manifest record, governance case, or public mirror references this artifact, it should cite the Admissibility Wiki page rather than recreating provenance authority locally.

Recommended reference text:

```text
The source-geometry provenance record for SG-001 is maintained by StegVerse-Labs/admissibility-wiki at docs/formalisms/original-drawing-reference.md. Publisher cites that record only as a public provenance source and does not independently establish derivation, priority, or admissibility.
```

## Boundary

Publisher may publish papers and public records that discuss the source geometry.

Publisher does not:

- establish custody authority for SG-001;
- prove that SG-001 caused BCAT/GCAT;
- prove formal derivation from the drawing;
- prove priority or originality claims;
- convert a provenance page into executable proof authority;
- replace Admissibility Wiki governance records;
- replace formalism-test receipts.

## Next Actions

1. When a paper directly discusses BCAT/GCAT history, add a citation to the Admissibility Wiki Original Drawing Reference page.
2. If the original photographs are committed as binary artifacts later, record hashes and custody fields in the Admissibility Wiki first.
3. Publisher should mirror only the reviewed public reference and should keep source authority with the Admissibility Wiki.
