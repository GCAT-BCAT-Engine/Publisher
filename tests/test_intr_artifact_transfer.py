from __future__ import annotations
import copy, json, tempfile, unittest
from datetime import datetime, timezone
from pathlib import Path

from publisher.intr_artifact_transfer import (
    PublisherArtifactTransferError, canonical_json, process_artifact_transfer,
    sha256_value, verify_artifact_return,
)

ROOT=Path(__file__).resolve().parents[1]

def bundle():
    value=json.loads((ROOT/"tests/fixtures/document-export/admitted.json").read_text())
    value["authorization"]["expires_at"]="2099-12-31T23:59:59Z"
    unhashed=copy.deepcopy(value); unhashed.pop("export_sha256",None)
    value["export_sha256"]=sha256_value(unhashed)
    return value

def transfer():
    b=bundle()
    return {
      "schema":"stegverse.publisher.artifact-transfer/v1",
      "transfer_id":"kv-publisher-transfer-test-001","operation":"TRANSFER",
      "export_bundle":b,"export_sha256":b["export_sha256"],
      "requested_formats":b["requested_formats"],
      "authorization_ref":b["authorization"]["authority_ref"],
      "publication_authorized":False,"release_authorized":False,
      "execution_authorized":False,"authority_effect":"NONE",
    }

class PublisherArtifactTransferTests(unittest.TestCase):
    def test_exact_transfer_renders_and_returns_reconstructable_artifacts(self):
        raw=canonical_json(transfer()).encode()
        with tempfile.TemporaryDirectory() as td:
            result, returned=process_artifact_transfer(raw,Path(td))
        parsed=verify_artifact_return(returned)
        self.assertEqual(parsed,result)
        self.assertFalse(result["publication_authorized"])
        self.assertEqual({x["format"] for x in result["artifacts"]},set(bundle()["requested_formats"]))

    def test_noncanonical_transfer_bytes_rejected(self):
        raw=(json.dumps(transfer(),indent=2)+"\n").encode()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PublisherArtifactTransferError):
                process_artifact_transfer(raw,Path(td))

    def test_authority_expansion_rejected(self):
        value=transfer(); value["publication_authorized"]=True
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(PublisherArtifactTransferError):
                process_artifact_transfer(canonical_json(value).encode(),Path(td))

if __name__=="__main__": unittest.main()
