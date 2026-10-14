# AegisFlow external inventory integration

## Purpose

AegisFlow is an interoperability and coordination layer, not a replacement for a participating hospital's HIS/ERP/POS. Each participating facility designates one authoritative inventory feed for the prototype. The source sends a minimal batch-level availability snapshot; AegisFlow does not request patient records or full internal purchase/finance ledgers.

The current endpoint is a tested prototype contract. Registering a source does **not** install a real HL7/FHIR/ERP adapter. A connector for each partner system still must be implemented and validated with that system's team.

## Admin onboarding

1. Sign in as a System Admin and open **Integrations**.
2. Register a source name, system type and facility. AegisFlow issues a random integration key and stores only its SHA-256 hash.
3. Copy the key at creation. The key is shown only once.
4. Create medicine mappings from the partner's external medicine code to the canonical AegisFlow medicine ID. A snapshot with any unmapped medicine code is rejected as a whole.
5. Configure the partner server to post inventory snapshots to the gateway using the `X-Integration-Key` header.
6. Use **Rotate key** if the key is lost or compromised. Rotation invalidates the previous key. **Disable** immediately blocks that feed; rotate to re-enable with a new key.

Only System Admins can create or disable integration sources and configure mappings. Each key is restricted to a single facility. The database enforces a single integration source per facility in this prototype.

## Endpoints

All paths below are relative to `/api/v1`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/integrations/sources` | Create source; return the one-time key |
| GET | `/integrations/sources` | List sources (System Admin only) |
| POST | `/integrations/sources/{source_id}/disable` | Disable a key |
| POST | `/integrations/sources/{source_id}/rotate-key` | Re-enable/rotate key and return the new key once |
| GET | `/integrations/sources/{source_id}/medicine-mappings` | List code mappings |
| POST | `/integrations/sources/{source_id}/medicine-mappings` | Create or update a code mapping |
| POST | `/integrations/inventory/snapshot` | Ingest a batch-level inventory snapshot |

The snapshot endpoint authenticates with `X-Integration-Key`, not the user JWT. Do not place this key in public client-side code, source control, logs or a browser application.

## Snapshot payload

Example for one medicine across two batches:

```json
{
  "external_event_id": "apollo-chennai-inventory-2026-10-14-101500",
  "source_timestamp": "2026-10-14T10:15:00+05:30",
  "items": [
    {
      "external_medicine_code": "INSULIN-100IU-10ML",
      "total_stock": 110,
      "minimum_threshold": 20,
      "reorder_threshold": 30,
      "daily_consumption_rate": 3.5,
      "lead_time_days": 2,
      "batches": [
        {
          "batch_number": "INS-ABC-2606",
          "manufacturing_date": "2026-06-01",
          "expiry_date": "2027-06-01",
          "quantity_received": 100,
          "available_stock": 80,
          "reserved_stock": 10,
          "supplier_name": "Example Supplier",
          "unit_cost": 60
        },
        {
          "batch_number": "INS-XYZ-2609",
          "manufacturing_date": "2026-09-01",
          "expiry_date": "2027-09-01",
          "quantity_received": 30,
          "available_stock": 20,
          "reserved_stock": 0,
          "supplier_name": "Example Supplier",
          "unit_cost": 60
        }
      ]
    }
  ]
}
```

The example is synthetic. In a real adapter, use the partner's real batch IDs, timestamps and medicine mapping. Do not send an example payload as a real stock statement.

Validation rules:

- `external_event_id` must be stable for a single snapshot; `source_timestamp` must include a timezone.
- Each medicine line may occur once per snapshot. Each batch number may occur once per medicine line.
- `total_stock` must equal the sum of source-reported batch available plus externally reserved quantities.
- A non-zero stock line must include batch expiry data; expiry date cannot precede manufacturing date.
- Each external medicine code must have an active mapping to an AegisFlow medicine.
- A new snapshot timestamp must be newer than the last accepted timestamp. Snapshots more than five minutes in the future are rejected.
- AegisFlow's own active transfer reservations are preserved. The partner's available quantity is treated as pre-AegisFlow-reservation availability; inventory totals are reconciled in the transaction.

## Replay and failure behavior

The database stores a unique receipt for each `(source_id, external_event_id)` along with a canonical payload hash. Repeating the same event ID with the same payload returns an idempotent replay response without changing inventory again. Reusing an event ID with different content is rejected. Snapshot data, batch updates and the receipt are committed in one transaction so validation failures roll back the entire snapshot.

A rejected snapshot does not partially apply its other medicine lines. The caller should record the response and remediate the mapping, batch or timestamp problem before sending a corrected snapshot with a new event ID.

## What this prototype does not claim

- No real vendor integration, HL7/FHIR parser, polling agent, webhook subscription or CSV scheduler is installed yet. `system_type` classifies the partner feed; it does not implement the adapter.
- No patient-level data is ingested.
- The snapshot is supplied by the partner; AegisFlow does not independently verify that the source's physical stock count is accurate.
- Cold-chain capability is a declared facility attribute, not real-time temperature telemetry.
- A production rollout still needs TLS enforcement, partner credential custody and rotation procedures, rate limiting, integration monitoring, a retry/dead-letter strategy, partner-specific reconciliation and security validation.
