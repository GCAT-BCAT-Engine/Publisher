#!/usr/bin/env python3
import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data/rtg-tt/publication-ingestion.v0.1.json'
d=json.loads(p.read_text())
assert d['contract_version']=='rtg-tt-v0.1'
assert d['site_source']['commit']=='50d417b2dbf29d3812bdae8c3d1942b1ce5a5162'
assert d['stegcore_source']['commit']=='47cb26c513c9404017e650e025b8cc14eb02c41c'
assert d['status']=='VERIFIED_INGESTION_CANDIDATE'
assert d['mapping']=={'RESOLUTION_SATISFIED':'ALLOW','FAIL_CLOSED':'DENY','QUARANTINE':'DEFER'}
assert all(v is False for v in d['authority'].values())
print('RTG_TT_PUBLICATION_INGESTION_PASS')
