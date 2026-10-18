# Economic roadmap evidence export requests

Committing a `*.json` request here, on `main`, runs
`.github/workflows/economic-roadmap-evidence-export-request.yml`. That run validates every
listed closure record with `publisher/economic_roadmap_evidence_export.py` and commits
the public-safe projection `data/economy/economic-roadmap-evidence.v1.json`.

```json
{
  "schema": "stegverse.publisher.economic-evidence-export-request/v1",
  "goal_task_id": "ECOSYSTEM-ECONOMIC-WHITEPAPER-GATED-ROADMAP-001",
  "records": ["<stegverse.publisher.economic-benchmark-closure-input/v1 record>"]
}
```

Each record must carry an authenticated `master_records_closure` from the existing
closure path. A malformed request or a record that does not prove its closure is
refused with an exact failed predicate and is never exported. The projection never
grants benchmark completion: the Site can at most mark a fully evidenced benchmark
eligible for Publisher-governed review.
