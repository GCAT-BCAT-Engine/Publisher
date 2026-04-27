# GCAT-BCAT-Engine Publisher

> **Paper publishing, social media, and ecosystem coordination for the GCAT/BCAT research group.**

## Integration with AaCT-E

This repository ingests status reports from [AaCT-E/demo](https://github.com/AaCT-E/demo) to:

- Track verification health across releases
- Archive reproducible trace artifacts
- Coordinate social media announcements
- Link papers to executable evidence

## Quick Start

```bash
pip install -r requirements.txt
python scripts/ingest_aacte_status.py --status-file status.json
python scripts/social_media_scheduler.py --status-file status.json --dry-run
```

## Directory Structure

| Path | Purpose |
|------|---------|
| `scripts/ingest_aacte_status.py` | Parse AaCT-E status into dashboard DB |
| `scripts/social_media_scheduler.py` | Queue posts for milestones |
| `scripts/archive_traces.py` | Long-term trace archival |
| `templates/` | Social media post templates |
| `dashboard/` | HTML status dashboard |
| `.github/workflows/publisher-sync.yml` | Daily sync from AaCT-E CI |

## Ecosystem

- **Theory:** [GCAT-BCAT-Engine](https://github.com/GCAT-BCAT-Engine)
- **Demo:** [AaCT-E/demo](https://github.com/AaCT-E/demo)
- **Monitor:** [StegVerse-Labs/StegDB](https://github.com/StegVerse-Labs/StegDB)
- **SDK:** [StegVerse-Labs/SDK](https://github.com/StegVerse-Labs/SDK)
