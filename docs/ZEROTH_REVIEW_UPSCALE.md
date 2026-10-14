# AegisFlow — Zeroth Review Upgrade

## Product position

AegisFlow is a healthcare supply-network intelligence and emergency redistribution coordination layer. Participating organizations retain their existing HIS/ERP/POS and inventory systems. AegisFlow is intended to exchange controlled, minimal availability signals and coordinate sourcing, human approval, logistics and delivery across the network.

Do not describe the prototype as replacing an institution's inventory, billing, patient-management or procurement platform. Billing/payment processing is not part of this review slice.

## Implemented review vertical slice

1. **Shortage intelligence:** the Shortage Intelligence page reads a backend forecast API. The deterministic rule-based projection uses unreserved available stock, recorded daily consumption, replenishment lead time and the medicine's safety-stock days.
2. **Donor discovery:** candidate facilities must be active, carry the required medicine, have coordinates, be within the configured geographic radius, and have enough stock above their minimum threshold.
3. **Batch and expiry safety:** donor inventory must have unexpired, batch-traceable stock. The earliest-expiry date and eligible batch count are returned with the recommendation. Stock without batch-level traceability is excluded from new donor recommendations.
4. **Cold-chain safety:** medicine records can explicitly require cold-chain handling; facilities can declare cold-chain capability. A cold-chain requirement is a hard eligibility constraint rather than a score bonus.
5. **Explainable ranking:** the deterministic score exposes its component scores, weights, ranked order, suggested quantity and a human-readable reason. It is not a trained ML model or a probability of success.
6. **Multi-source request creation:** an emergency can produce one pending transfer leg per eligible donor until the remaining target quantity is covered or eligible supply is exhausted.
7. **Human decision:** a hospital administrator can approve the full or partial quantity or reject a request with a recorded reason. Approval rechecks aggregate stock and unexpired batch quantities inside a database transaction; batch lots are reserved FEFO.
8. **Logistics control:** an operations role must assign transport before dispatch. Dispatch and delivery are separate state transitions. Cold-chain medicines require declared capability at both facilities and a cold-chain transport type.
9. **Delivery settlement:** delivery confirmation changes donor and destination inventory in a transaction, preserves batch/expiry metadata at the destination, and updates emergency fulfillment. A retry after completion is a no-op.
10. **Role-scoped views:** emergency and transfer reads are limited to network operations roles or the assigned hospital; inventory records are scoped to assigned facilities for facility roles. The frontend gets the actual current role from `/auth/me`.
11. **Timeline:** the timeline combines recorded timestamps from emergency, transfer and dispatch records. It is a persisted-milestone timeline, not yet a complete append-only audit event stream.

## Scoring and forecasting limitations

- Geographic distance is calculated from coordinates as great-circle distance. It is not road distance, routing, traffic-aware ETA or a delivery-time guarantee.
- Donor ranking and stockout projections are explainable deterministic rules. No trained ML forecasting model is claimed.
- The stockout projection reports insufficient data when positive daily consumption is not recorded; it does not call missing consumption data “safe.”
- Cold-chain capability is a declared facility attribute. The prototype does not yet ingest live temperature telemetry or certify cold-chain compliance.
- Batch traceability is enforced for new emergency sourcing/approval, but old legacy transfers and inventory snapshots need reconciliation against batch records before a production rollout.
- Inventory integration with real external HIS/ERP/POS partners is not implemented or verified. A replay-safe integration gateway, partner credential management and per-source mapping are follow-up work.
- Production deployment still requires validated migrations, deployment configuration, monitoring, data retention and security review.

## Role responsibilities in the prototype

- **System Admin:** platform governance and network visibility.
- **Emergency Operator:** network emergency visibility, donor matching, request coordination, transport assignment, dispatch and delivery tracking.
- **Hospital Admin:** visibility into assigned hospital emergencies/inventory, transfer approval/rejection and incoming supply review.
- **Pharmacist / Shop Owner / Supplier:** facility-scoped inventory visibility. Dedicated supplier procurement/fulfillment workflows remain future work.

## Run locally for a live review

Use a disposable or backed-up development database before applying the new additive schema migrations.

Backend (from the backend directory, with the repository's environment configured):

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend (in a second terminal):

```bash
cd frontend
npm ci
npm run dev
```

Open the Vite URL shown in the terminal, sign in using a real user seeded in the configured backend database, and use the live API rather than any old browser tab/session. The default frontend API base is `http://localhost:8000/api/v1`; configure `VITE_API_URL` if your backend is hosted elsewhere.

## Recommended zeroth-review walkthrough

1. Sign in as an emergency operator or system administrator and open **Emergency Operations**.
2. Open a case, review backend-ranked donor candidates, inspect their score breakdown, eligible batch count, nearest expiry and cold-chain capability.
3. Create transfer requests. If no eligible batch-traceable stock is available, the application should say so rather than inventing donor options.
4. Sign in as the assigned destination Hospital Admin and open **Transfer Control**. Review and approve a full/partial quantity or reject with a reason.
5. Return as an operations role. Assign transport; for a cold-chain medicine, select a cold-chain vehicle. Dispatch the approved transfer.
6. Confirm delivery only after the shipment has physically arrived. Verify both inventories and the emergency's remaining quantity, then inspect the recorded timeline.
7. Open **Shortage Intelligence** to discuss projected stockout days, risk level, the reason, and the recommended action.

## Validation scenarios

- Invalid coordinates are rejected.
- A nearby donor with insufficient stock surplus is excluded.
- Expired lots and untracked aggregate-only inventory are excluded from new emergency sourcing.
- FEFO reserves the earliest-expiring eligible lots first.
- A cold-chain medicine does not match to facilities without declared capability.
- Hospital users cannot approve transfers for another hospital.
- Dispatch cannot precede approval and transport assignment.
- A normal vehicle cannot be assigned to a cold-chain medicine.
- Retrying delivery confirmation does not settle stock twice.
- Multi-source delivery resolves an emergency only when the receiving facility's available quantity reaches the requested target.
- A forecast without positive consumption data is reported as insufficient data.
