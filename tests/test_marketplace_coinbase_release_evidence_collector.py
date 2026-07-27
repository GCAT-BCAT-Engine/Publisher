from __future__ import annotations

import json

from scripts import collect_marketplace_coinbase_release_evidence as collector


def test_missing_token_writes_pending_credential(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "TOKEN", "")
    monkeypatch.setattr(collector, "OUTPUT", tmp_path / "status.json")
    result = collector.main()
    status = json.loads((tmp_path / "status.json").read_text())
    assert result == 0
    assert status["status"] == "PENDING_CREDENTIAL"
    assert status["paper_release_verified"] is False
    assert status["publication_authorized"] is False
    assert status["release_authorized"] is False
    assert status["execution_authorized"] is False
    assert status["live_authority_granted"] is False


def test_status_digest_is_bound(tmp_path, monkeypatch):
    monkeypatch.setattr(collector, "OUTPUT", tmp_path / "status.json")
    collector.write("REJECTED", "test", {"source": {"state": "INVALID"}}, ["bad"])
    status = json.loads((tmp_path / "status.json").read_text())
    body = {key: value for key, value in status.items() if key != "status_digest"}
    assert status["status_digest"] == collector.digest(body)
    assert status["manual_user_action_required"] is False
