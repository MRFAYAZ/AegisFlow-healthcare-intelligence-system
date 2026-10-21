# AegisFlow sample integration client

This directory contains a small standard-library Python client for demonstrating the external inventory snapshot API. It does not connect to a vendor system or read a real HIS/ERP database; an adapter must map a vendor's actual fields and identifiers to this contract.

## Prerequisites

1. The AegisFlow backend is running.
2. A System Admin registered an integration source for the test facility.
3. The partner medicine codes in the JSON payload have active mappings to AegisFlow medicine IDs.
4. The issued integration key is stored in an environment variable on the sending server.

## Run

PowerShell:

```powershell
$env:AEGISFLOW_API_URL = "http://localhost:8000/api/v1"
$env:AEGISFLOW_INTEGRATION_KEY = "<paste-key-in-your-local-terminal-only>"
python examples/integration_client/send_snapshot.py .\my_snapshot.json
```

Bash:

```bash
export AEGISFLOW_API_URL="http://localhost:8000/api/v1"
export AEGISFLOW_INTEGRATION_KEY="<paste-key-in-your-local-terminal-only>"
python examples/integration_client/send_snapshot.py ./my_snapshot.json
```

The script sends `POST /integrations/inventory/snapshot` with the `X-Integration-Key` header, prints the API result, and never prints the key. Use a source-specific key from a disposable development database while demonstrating.

## Payload checklist

- A stable `external_event_id` for each snapshot and a timezone-aware `source_timestamp`.
- One row per mapped partner medicine code.
- Non-zero stock must include lot/batch numbers and expiry/manufacturing dates.
- The total is the sum of the source-reported batch available and externally reserved quantities.
- Include real, reconciled values only. Replaying the same event ID with identical content is a no-op; reusing it with changed content is rejected.

See [EXTERNAL_INTEGRATION.md](../../docs/EXTERNAL_INTEGRATION.md) for the full request shape and limitations.

**Adoption boundary:** this is an API client example, not a prebuilt HL7/FHIR, pharmacy POS, ERP, or CSV connector. Partner adapters require their own field mapping, credentials, retries, monitoring and validation with the participating organization.
