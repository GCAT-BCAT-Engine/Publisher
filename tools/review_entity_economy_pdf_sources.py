#!/usr/bin/env python3
"""Non-authorizing editorial transport: retrieve and verify two public Entity Economy PDFs.

This validation script fetches public Site bytes from a fixed Git commit, rejects
wrong identities, and writes page-addressable extracted text and a source manifest.
It cannot authorize publication, AI execution, settlement, or benchmark progression.
"""
from __future__ import annotations
import base64, hashlib, json, pathlib, re, subprocess, urllib.request, zlib

SITE_COMMIT = "760cdd027e7507c027e0928fcd127b5a47e70a15"
BASE = f"https://raw.githubusercontent.com/StegVerse-Labs/Site/{SITE_COMMIT}/papers/"
EXPECTED = {
  "volume_i": {"sha256": "a831891cee4c4e7a920ed6d38090672e0722b434a5941632620c3e11d8e4da95", "size": 16647, "pages": 9},
  "volume_ii": {"sha256": "129accea04dcef0c5b063ae5799d9952e97462859fb36842c93a3ca7776fe95f", "size": 132330, "pages": 7}
}
OUT = pathlib.Path("entity-economy-original-pdf-review")

def read(path: str) -> bytes:
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "StegVerse-Publisher-editorial-validator/1"})
    with urllib.request.urlopen(req, timeout=45) as reply:
        return reply.read()

def check(label: str, payload: bytes, dest: pathlib.Path) -> dict:
    assert payload.startswith(b"%PDF-"), f"{label}: PDF header missing"
    assert b"%%EOF" in payload[-2048:], f"{label}: PDF EOF missing"
    actual = {"sha256": hashlib.sha256(payload).hexdigest(), "size": len(payload)}
    expected = EXPECTED[label]
    assert actual["sha256"] == expected["sha256"], f"{label}: source digest mismatch {actual}"
    assert actual["size"] == expected["size"], f"{label}: source length mismatch {actual}"
    pdf = dest / f"{label}.pdf"
    pdf.write_bytes(payload)
    info = subprocess.check_output(["pdfinfo", str(pdf)], text=True, stderr=subprocess.PIPE)
    match = re.search(r"(?m)^Pages:\\s*(\\d+)", info)
    assert match, f"{label}: PDF page count unavailable"
    pages = int(match.group(1))
    assert pages == expected["pages"], f"{label}: expected {expected['pages']} pages; got {pages}"
    text_path = dest / f"{label}.txt"
    result = subprocess.run(["pdftotext", "-layout", str(pdf), str(text_path)], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f"{label}: pdftotext failed ({result.returncode}): {result.stderr[-2000:]}")
    page_text = [p for p in text_path.read_text().split("\\f") if p.strip()]
    assert len(page_text) == pages, f"{label}: extracted {len(page_text)} of {pages} pages"
    for n, page in enumerate(page_text, 1):
        (dest / f"{label}_page_{n:02d}.txt").write_text(page)
        print(f"=== {label.upper()} PAGE {n}/{pages} ===", flush=True)
        print(page[:15000], flush=True)
    print(f"VERIFIED_SOURCE_PDF {label} pages={pages} sha256={actual['sha256']}", flush=True)
    return {"label":label,"source_commit":SITE_COMMIT,**actual,"pages":pages,"extraction":"poppler-pdftotext-layout"}

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    first = read("stegverse-entity-economy/stegverse-entity-economy.pdf")
    meta = [check("volume_i", first, OUT)]
    prefix = "".join(read(f"stegverse-entity-economy-volume-ii/artifact/volume-ii.part{i:02d}.b64").decode("ascii").split() for i in range(17))
    prefix_bytes = base64.b64decode(prefix, validate=True)
    tail = zlib.decompress(read("stegverse-entity-economy-volume-ii/artifact/volume-ii.tail-after-part16.deflate"))
    meta.append(check("volume_ii", prefix_bytes + tail, OUT))
    (OUT / "verified_source_manifest.json").write_text(json.dumps(meta,indent=2)+"\n")
    print("EDITORIAL_PDF_SOURCE_TRANSPORT_PASS",flush=True)

if __name__ == "__main__":
    main()
