# Vault → Publisher Integration Spec

## Purpose

Define how opt-in data from continuity-vault-kit users flows into Publisher datasets for research aggregation and revenue sharing.

## Data flow

```
continuity-vault-kit user
    ├── opts in via _Policy/Data_Sharing_Policy.md
    ├── selects categories to share
    └── data is marked for aggregation

          ↓ (weekly batch)

Publisher vault-data-ingestion workflow
    ├── reads batch from vault ingestion endpoint
    ├── anonymizes and aggregates
    ├── validates dataset quality
    └── creates dataset for licensing

          ↓ (on use)

Revenue distribution
    ├── dataset is licensed/sold
    ├── revenue calculated at dataset level
    └── contributors receive proportional share
```

## Ingestion endpoint

**Source:** `continuity-vault-kit` ingestion endpoint  
**Target:** `GCAT-BCAT-Engine/Publisher` vault-data-ingestion workflow  
**Frequency:** Weekly (Sundays 12:00 UTC)  
**Format:** JSON batch with anonymized, aggregated data

## Batch format

```json
{
  "schema_version": "1.0.0",
  "batch_id": "uuid",
  "source": "continuity-vault-kit",
  "date_range": {
    "start": "2026-04-18",
    "end": "2026-04-24"
  },
  "aggregation": {
    "user_count": 150,
    "total_notes": 3200,
    "total_media_files": 450,
    "categories": ["01_Notes", "02_Research", "04_Media"]
  },
  "datasets": [
    {
      "dataset_id": "events_2026_04",
      "type": "temporal_patterns",
      "content": "aggregated_event_types_and_frequencies",
      "contributor_count": 89
    },
    {
      "dataset_id": "research_interests_2026_04",
      "type": "interest_mapping",
      "content": "aggregated_research_topics_and_sources",
      "contributor_count": 67
    }
  ],
  "privacy_verification": {
    "anonymization_check": "passed",
    "minimum_aggregation_size": "passed",
    "no_restricted_content": "passed"
  }
}
```

## Revenue sharing flow

1. **Dataset creation** — Publisher creates aggregate dataset
2. **Dataset licensing** — Dataset is licensed to research/commercial entity
3. **Revenue calculation** — Total revenue calculated at dataset level
4. **Contribution scoring** — Each user's share based on volume, uniqueness, quality
5. **Payout** — Periodic distribution to contributors with valid payout methods

## Governance events

| Event | Emitted by | Purpose |
|-------|-----------|---------|
| `publisher.data_ingest` | Publisher | Log batch ingestion |
| `publisher.dataset_created` | Publisher | Dataset available for licensing |
| `publisher.dataset_used` | Publisher | Dataset licensed or sold |
| `publisher.revenue_distributed` | Publisher | Payouts sent to contributors |
| `vault.user_opted_in` | continuity-vault-kit | User joined sharing program |
| `vault.user_opted_out` | continuity-vault-kit | User left sharing program |

## Safety

- Individual data never exposed
- `03_Records/` permanently excluded
- `_Policy/` files never ingested
- `Privacy Level: restricted` files skipped
- Users can audit their sharing status anytime
- Withdrawal stops future sharing immediately
