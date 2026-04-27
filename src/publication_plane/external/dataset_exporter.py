"""
Open data catalog export.
Publishes datasets to external catalogs with full provenance.
"""

import json
from pathlib import Path
from typing import Dict, Any

from stegverse_core_lite.receipt.id import DeterministicReceiptID
from stegverse_core_lite.hash.deterministic import DeterministicHash


class DatasetExporter:
    """
    Exports datasets to open data catalogs with StegVerse provenance.
    """

    def __init__(self, catalog_dir: str = "catalog"):
        self.catalog_dir = Path(catalog_dir)
        self.catalog_dir.mkdir(parents=True, exist_ok=True)

    def export(
        self,
        dataset: Dict[str, Any],
        metadata: Dict[str, Any],
        seed: str = "default"
    ) -> Dict[str, Any]:
        """
        Export dataset with provenance metadata.
        """
        # Hash dataset content
        canonical = json.dumps(dataset, sort_keys=True)
        content_hash = DeterministicHash.hash(canonical, seed)

        # Generate receipt
        receipt_id = DeterministicReceiptID().derive({
            "content_hash": content_hash,
            "metadata": metadata,
        }, seed)

        catalog_entry = {
            "receipt_id": receipt_id,
            "content_hash": content_hash,
            "metadata": metadata,
            "schema": "stegverse-catalog-v1",
            "seed": seed,
        }

        path = self.catalog_dir / f"{receipt_id}.json"
        path.write_text(json.dumps(catalog_entry, indent=2), encoding="utf-8")

        return {
            "receipt_id": receipt_id,
            "catalog_path": str(path),
            "content_hash": content_hash,
        }


def main():
    exporter = DatasetExporter()

    dataset = {"samples": 10000, "features": ["x", "y", "z"], "source": "sandbox"}
    metadata = {"title": "Demo Dataset", "license": "CC-BY-4.0"}

    result = exporter.export(dataset, metadata, "catalog-demo-001")
    print(f"Receipt: {result['receipt_id']}")
    print(f"Catalog: {result['catalog_path']}")


if __name__ == "__main__":
    main()
