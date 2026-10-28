"""Deterministic hashing and receipt IDs, carried in-repo (no external dependency).

These three classes are copied verbatim from GCAT-BCAT-Engine/core-lite at bc999df
(package stegverse-core-lite), which Publisher previously required at install time:
  src/stegverse_core_lite/hash/deterministic.py   sha256 3090b21543fdf6b75cf03790c21a988baa9e6c6b3a8db9e9bbecf15cd375007d
  src/stegverse_core_lite/receipt/id.py           sha256 4996cfbe87eefcad99298b92d6f32f8a9e9e9d6051fa46f6d846670c00ab60fe
  src/stegverse_core_lite/interfaces/protocols.py sha256 52b0a0b91cb5166fc169fb83d0dcafccb84edfe99d60e5afba4b72d858e6f341
Class bodies are unchanged, so receipt IDs and hashes are byte-identical to the package's.
Standard library only. Goal StegVerse-org/.github#164 (dependency reduction).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, Protocol, runtime_checkable


class DeterministicHash:
    """
    SHA256-based deterministic hashing.
    Same content + same seed = same hash, always.
    """

    ALGORITHM = "sha256"

    @classmethod
    def hash(cls, content: str, seed: str = "") -> str:
        """Generate deterministic hash from content and seed."""
        composite = f"{content}::{seed}"
        return hashlib.sha256(composite.encode("utf-8")).hexdigest()

    @classmethod
    def hash_dict(cls, content: Dict[str, Any], seed: str = "") -> str:
        """Hash a dictionary by canonicalizing it first."""
        import json
        canonical = json.dumps(content, sort_keys=True, ensure_ascii=True)
        return cls.hash(canonical, seed)

    @classmethod
    def verify(cls, content: str, seed: str, expected_hash: str) -> bool:
        """Verify content matches expected hash."""
        return cls.hash(content, seed) == expected_hash

    @classmethod
    def verify_dict(cls, content: Dict[str, Any], seed: str, expected_hash: str) -> bool:
        """Verify dictionary matches expected hash."""
        return cls.hash_dict(content, seed) == expected_hash


class DeterministicReceiptID:
    """
    Generates deterministic, verifiable receipt IDs.
    Same content + same seed = same receipt ID, always.
    """

    def __init__(self, hash_provider=None):
        self.hash_provider = hash_provider or DeterministicHash()

    def derive(self, content: Dict[str, Any], seed: str) -> str:
        """Generate deterministic receipt ID."""
        canonical = json.dumps(content, sort_keys=True, ensure_ascii=True)
        full_hash = self.hash_provider.hash(canonical, seed)
        return full_hash[:32]  # 32-char truncated ID

    def verify(self, receipt_id: str, content: Dict[str, Any], seed: str) -> bool:
        """Verify receipt ID matches content."""
        derived = self.derive(content, seed)
        return derived == receipt_id

    def derive_full(self, content: Dict[str, Any], seed: str) -> str:
        """Generate full 64-char receipt hash (for high-security contexts)."""
        canonical = json.dumps(content, sort_keys=True, ensure_ascii=True)
        return self.hash_provider.hash(canonical, seed)


@runtime_checkable
class ReceiptIDProvider(Protocol):
    """Deterministic receipt ID generation and verification."""

    def derive(self, content: Dict[str, Any], seed: str) -> str: ...
    def verify(self, receipt_id: str, content: Dict[str, Any], seed: str) -> bool: ...
