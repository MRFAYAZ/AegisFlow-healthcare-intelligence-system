# AegisFlow Product Surface

AegisFlow uses shared platform capabilities with role-based workspaces. A role changes the user's navigation, landing route, and permitted routes; it does not create a separate application.

## Current workspaces

| Role | Workspace | Landing route | Current capabilities |
| --- | --- | --- | --- |
| System admin | Governance workspace | `/dashboard` | Network visibility, emergency operations, transfers, dispatch oversight, analytics, map |
| Hospital admin | Hospital operations | `/dashboard` | Emergency response, inventory, shortage visibility, transfers, analytics, map |
| Emergency operator | Emergency operations center | `/emergency` | Emergency cases, shortages, transfers, dispatch coordination, map, analytics |
| Dispatcher | Logistics control tower | `/dispatcher` | Dispatch queue, transport assignment, active transfer control, map |
| Pharmacist | Donor operations | `/inventory` | Inventory, shortages, transfer requests, supply requests |
| Shop owner | Donor operations | `/inventory` | Inventory, transfers, supply requests |
| Supplier manager | Supply operations | `/inventory` | Supply inventory, shortages, transfers, network intelligence |
| Network participant | Existing role workspace | Existing role landing | Opt-in availability sharing, source discovery, and integration snapshot synchronization |

The source of truth for this policy is `frontend/src/auth/rolePermissions.ts`.

## Core operational story

```text
Shortage -> Emergency -> Donor matching -> Allocation -> Hospital approval
-> Inventory reservation -> Dispatch -> Delivery -> Inventory settlement -> Resolution
```

## Network intelligence and interoperability

AegisFlow is a coordination layer over facility systems, not a replacement for HIS, ERP, or pharmacy POS workflows. The current integration contract accepts authenticated, timestamped availability snapshots at `PUT /api/v1/integrations/facilities/{facility_id}/availability`. It updates only facility/medicine stock figures, rejects stale snapshots, and writes an audit event. It does not accept patient data, contracts, or purchase prices.

Facilities are hidden from Network Exchange until a facility-authorized user enables `network_visibility_enabled`. `POST /api/v1/network-exchange/search` returns only request-scoped offers: facility identity, safe transferable quantity, distance, score, batch traceability availability, and cold-chain eligibility. Donor safety stock, batch expiry/status, facility cold-chain capability, and search radius constrain eligibility. Cold-chain-required stock without batch records is ineligible. This version checks facility capability, not live temperature telemetry. Search never reserves or transfers inventory; allocation approval and dispatch remain separate human-controlled workflows.

Emergency operators and system administrators may explicitly request an emergency visibility override. The override is audited, still applies quantity, expiry, cold-chain, and distance checks, and does not authorize a transfer.

The current schema does not yet associate facilities with parent organizations or partner-network policies. Consequently, this release ranks by fulfillment and proximity without corporate ownership bias, but it cannot enforce internal/partner/external tiers or organization-level caps. Those policies require an organization and membership model before they can be represented as enforceable controls. CSV adapters, service-account credentials, webhook delivery, FHIR conformance, supplier demand forecasts, logistics ETA, and network simulation remain subsequent integration/pilot work and are not claimed as implemented.

## Deliberately deferred

These require backend contracts before they appear in navigation:

- System administration: organizations, users, permissions, configuration
- Procurement: catalog, purchase orders, supplier fulfillment
- Compliance: audit dashboard, exception reports, compliance exports
- Command finance: cost impact, logistics cost, procurement cost avoided
- Billing, payment gateways, patient billing, and insurance claims

The product should expose a new page only when its data ownership, authorization, and workflow are implemented end to end.
