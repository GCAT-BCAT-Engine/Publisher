#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from publisher.intr_artifact_transfer import PublisherArtifactTransferError, process_artifact_transfer, sha256_bytes

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("payload",type=Path)
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--return-packet",type=Path,required=True)
    a=p.parse_args()
    try:
        result, raw=process_artifact_transfer(a.payload.read_bytes(),a.output_dir)
        a.return_packet.parent.mkdir(parents=True,exist_ok=True)
        if a.return_packet.exists() and a.return_packet.read_bytes()!=raw:
            raise PublisherArtifactTransferError("immutable return packet conflict")
        a.return_packet.write_bytes(raw)
    except (OSError,PublisherArtifactTransferError) as exc:
        print("PUBLISHER_INTR_TRANSFER_REJECTED: "+str(exc),file=sys.stderr); return 1
    print(json.dumps({"state":"GENERATED_VALIDATED_NOT_PUBLISHED","transfer_id":result["transfer_id"],"return_sha256":sha256_bytes(raw),"formats":[x["format"] for x in result["artifacts"]]},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
