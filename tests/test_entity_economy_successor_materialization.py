import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REC=ROOT/"data/economy/entity-economy-successor-materialization.v1.json"
EXPECTED={"I":("stegverse-entity-economy-volume-i-2026-09-29-convergence","a831891cee4c4e7a920ed6d38090672e0722b434a5941632620c3e11d8e4da95"),"II":("stegverse-entity-economy-volume-ii-2026-09-29-convergence","129accea04dcef0c5b063ae5799d9952e97462859fb36842c93a3ca7776fe95f")}
def test_materialized_successors():
 r=json.loads(REC.read_text()); assert r["publication_executed"] is False and r["site_propagation_executed"] is False and r["historical_artifacts_immutable"] is True; assert len(r["artifacts"])==2
 for a in r["artifacts"]:
  eid,pred=EXPECTED[a["volume"]]; assert a["edition_id"]==eid and a["historical_predecessor_sha256"]==pred and a["historical_predecessor_mutation_permitted"] is False; b=(ROOT/a["path"]).read_bytes(); assert hashlib.sha256(b).hexdigest()==a["sha256"]; assert pred.encode() in b; assert b"MATERIALIZED_SOURCE_NOT_PUBLISHED" in b
 assert r["artifacts"][0]["path"]!=r["artifacts"][1]["path"] and r["artifacts"][0]["sha256"]!=r["artifacts"][1]["sha256"]
