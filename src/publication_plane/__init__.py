"""
Publication Plane for StegVerse Publisher.
==========================================

Cross-org publication orchestration with:
- Deterministic receipt generation (via stegverse-core-lite)
- Governed publication gating (via stegverse-core-full)
- StegDB pre-transition monitoring
- Multi-channel release routing
- Demo surface synchronization
- Evidence and audit trail management

Install: pip install stegverse-publisher
Requires: stegverse-core-lite, stegverse-core-full
"""

__version__ = "1.0.0"
__all__ = ["core", "routing", "surfaces", "external", "health"]
