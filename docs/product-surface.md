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

The source of truth for this policy is `frontend/src/auth/rolePermissions.ts`.

## Core operational story

```text
Shortage -> Emergency -> Donor matching -> Allocation -> Hospital approval
-> Inventory reservation -> Dispatch -> Delivery -> Inventory settlement -> Resolution
```

## Deliberately deferred

These require backend contracts before they appear in navigation:

- System administration: organizations, users, permissions, configuration
- Procurement: catalog, purchase orders, supplier fulfillment
- Compliance: audit dashboard, exception reports, compliance exports
- Command finance: cost impact, logistics cost, procurement cost avoided
- Billing, payment gateways, patient billing, and insurance claims

The product should expose a new page only when its data ownership, authorization, and workflow are implemented end to end.
