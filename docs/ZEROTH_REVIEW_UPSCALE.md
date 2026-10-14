# AegisFlow — Zeroth Review Upgrade

## Product position

AegisFlow is intended to operate as a healthcare supply-network intelligence and coordination layer. Participating organizations keep their existing HIS/ERP/POS systems; AegisFlow consumes controlled availability signals and coordinates cross-organization sourcing, allocation, approval and delivery.

It must not be described as replacing each organization's inventory, billing or patient-management application.

## Review-ready vertical slice

The first review should demonstrate one measurable workflow:

1. An affected facility has a shortage for a medicine.
2. AegisFlow searches active facilities carrying that medicine.
3. Donor candidates are filtered by transferable quantity and the donor's minimum-stock threshold.
4. Candidate distances are calculated from their stored coordinates (great-circle distance, explicitly not road ETA).
5. Candidates are ranked with a deterministic, explainable score and each recommendation includes a score breakdown and suggested quantity.
6. An authorized operator/hospital workflow creates and approves a transfer.
7. Dispatch and delivery are distinct lifecycle events.
8. Delivery settles inventory atomically and updates emergency fulfillment based on all completed transfer quantities.
9. External inventory systems can submit authenticated, replay-safe snapshots through an integration gateway.

## Adoption design

- Keep the institution's existing system as its operational source of truth.
- Prefer API/webhook integrations where available; support CSV/manual onboarding as a subsequent adapter.
- Share only network-relevant availability and safety attributes, not patient data or complete commercial inventory by default.
- A stable source event identifier and source timestamp are required for reliable integration retries and stale-event control.
- Do not allow organization preference, distance or match score to override hard safety constraints.

## Scope boundaries for the academic prototype

- Geospatial distance is a straight-line estimate; it must not be presented as driving distance or guaranteed ETA.
- Donor ranking is an explainable deterministic scoring engine, not a trained ML model.
- Any future demand forecast must disclose its inputs, assumptions, and evaluation metrics.
- A live production healthcare integration is not claimed unless tested against a real partner system.
- All schema changes require new Alembic migrations; historical migrations must not be rewritten.

## Proposed validation scenarios

- A nearby donor with insufficient safe stock is excluded.
- A farther donor with sufficient safe stock remains eligible.
- Equal-capacity facilities rank based on actual coordinates rather than a placeholder distance.
- Invalid coordinates fail clearly.
- Replaying an identical source event does not apply the same inventory update twice.
- Reusing an event ID with different content is rejected.
- Invalid dispatch state transitions are rejected.
- Retrying delivery confirmation does not settle stock twice.
- Multi-source delivery resolves an emergency only when cumulative completed quantity satisfies demand.
