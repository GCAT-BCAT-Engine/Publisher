# Marketplace–Coinbase Settlement Publication Contract v1

## Purpose

Define Publisher ingestion and public-display requirements for verified paper-mode settlement packets and Marketplace acknowledgement receipts.

## Required Inputs

- crypto-bot settlement export packet;
- verified packet digest;
- Marketplace acknowledgement receipt with `ACCEPTED` or `DUPLICATE`;
- exact intent digest and StegFin capital-review digest;
- receipt-chain head;
- paper release identifier and evidence references.

## Publication Rules

Publisher must display:

- paper-mode status;
- intent, review, packet, and acknowledgement digests;
- execution and settlement status;
- evidence links;
- verification timestamp;
- explicit statement that live Coinbase authority is not granted.

Publisher must refuse publication when Marketplace acknowledgement is absent or rejected, digests disagree, evidence is incomplete, or the packet claims live authority.

## Boundary

Publication communicates verified evidence. It does not activate trading, create financial authority, transfer assets, or replace Marketplace, StegFin, or crypto-bot determinations.
