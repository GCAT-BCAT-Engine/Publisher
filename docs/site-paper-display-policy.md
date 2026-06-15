# Site Paper Display Policy and Update Protocol

## Purpose

This policy defines how the StegVerse Site should display Publisher papers and governance case studies.

The Site should not become a separate editorial source of truth. It should display current Publisher records only after those records have passed the applicable Publisher validation and publication rules.

## Source of Truth

Publisher remains the source of truth for paper and governance case publication state.

The Site may display paper summaries, links, featured items, and current-publication lists, but it should derive those displays from Publisher-controlled records.

Current Publisher-controlled records include:

```text
papers_manifest.yml
papers.json
cases/<CASE-ID>.md
governance/cases/<CASE-ID>.case.json
governance/cases/<CASE-ID>.sources.json
governance/receipts/<CASE-ID>.receipt.json
```

## Display Eligibility

A paper or case may be displayed on Site when its Publisher record is present and its publication posture is explicit.

For papers, Site display should prefer records marked:

```text
published
featured
under_review
```

Draft records may be linked only from draft, preview, or internal review surfaces.

For governance cases, Site display should preserve the Publisher boundary posture. A public case may be listed as a case study, but not as a final factual finding unless the Publisher record explicitly says so.

## Required Update Sequence

Use this order when updating papers or governance case visibility:

```text
1. Update Publisher source record.
2. Validate Publisher record.
3. Generate or refresh Publisher runtime data.
4. Update Site display surface.
5. Verify Site links resolve to Publisher-owned paths.
6. Commit Site update with Publisher source reference.
```

## Current Paper Refresh Protocol

When Site needs the current paper list:

```text
1. Read Publisher papers_manifest.yml.
2. Regenerate Publisher papers.json if needed.
3. Confirm paper status and featured flags.
4. Display only eligible records on Site.
5. Preserve direct links back to Publisher paper pages or Publisher case pages.
```

## Governance Case Refresh Protocol

When Site displays governance case studies:

```text
1. Confirm public case Markdown exists under cases/.
2. Confirm machine case object exists under governance/cases/.
3. Confirm source manifest exists under governance/cases/.
4. Confirm receipt exists under governance/receipts/.
5. Run Publisher validation.
6. Display the case with its admissibility posture visible.
```

## Site Boundary Rules

The Site may summarize Publisher records.

The Site may not silently upgrade a draft, unresolved case, provisional record, or review posture into a stronger claim.

The Site may not hide admissibility posture when displaying governance cases.

The Site may not treat a public narrative as a final governance conclusion unless the Publisher record already carries that conclusion.

## Required Site Display Fields

For papers, Site should display at minimum:

```text
title
subtitle or abstract summary
status
version
date
category
tags
link to Publisher page
```

For governance cases, Site should display at minimum:

```text
case_id
title
event_date or observed_date
case_type
evidence_posture
admissibility_status
link to Publisher case page
```

## Update Receipt Expectation

Any Site update that changes visible paper or governance case listings should reference the Publisher record or commit that justified the display change.

A Site display change is not the authority source. It is a presentation update derived from Publisher-controlled records.

## Failure Conditions

Do not update Site display if:

```text
Publisher validation fails
Publisher source record is missing
paper status is ambiguous
governance case posture is missing
links resolve to non-Publisher-controlled copies
Site text strengthens a Publisher claim without a matching Publisher record change
```

## Done State

A Site paper display update is done when:

```text
Publisher source record is valid
Site display matches Publisher status
links resolve to Publisher-owned paths
admissibility posture is preserved for governance cases
commit message references the Publisher source update
```
