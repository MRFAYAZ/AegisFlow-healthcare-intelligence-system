# AegisFlow — First Review Demonstration Runbook

**Milestone:** First Review  
**Target outcome:** demonstrate one complete, reproducible, multi-facility emergency redistribution workflow.

This runbook is a verification plan. A checklist item is not considered complete merely because an API route or UI component exists; it must be exercised against a running application and recorded as passed.

## 1. Review narrative

Present AegisFlow as a healthcare supply-network coordination prototype:

> Participating facilities retain their existing inventory systems. AegisFlow receives a limited, authorized inventory feed, validates and reconciles it, estimates stockout risk, identifies eligible donor facilities, and coordinates a human-approved transfer with an auditable operational timeline.

Do not describe the current ranking or stockout projection as trained AI/ML. The donor engine is deterministic weighted ranking; the stockout engine is rule-based. Historical demand forecasting is a planned ML milestone.

## 2. Required demonstration scenario

Use a clearly labelled synthetic dataset. Do not present fabricated facilities, stock values or results as real partner data.

### Scenario

- Requesting facility: Demo Hospital A.
- Donor candidates: Demo Hospital B and Demo Pharmacy C.
- Product: one batch-traceable medicine with a canonical AegisFlow medicine record.
- Emergency: requesting facility has insufficient usable stock for the scenario's required quantity.
- Donor B: nearer, with sufficient verified transferable quantity.
- Donor C: farther away or with a smaller safe surplus.
- Safety exclusion: include one deliberately ineligible candidate (expired/untraceable batch or incompatible cold-chain capability) to prove that hard eligibility filters run before ranking.

Create a second product record for an Ayurvedic product only after its category metadata and applicable validation rules have been implemented. Do not use conventional medicine expiry or cold-chain assumptions blindly for every Ayurvedic product; validate product-specific requirements with authoritative domain guidance.

## 3. Live demonstration sequence

### A. Application and database readiness

- [ ] Frontend starts successfully.
- [ ] FastAPI starts successfully and OpenAPI docs load.
- [ ] PostgreSQL/PostGIS container is healthy.
- [ ] Alembic reports the expected head revision.
- [ ] Login works with a seeded demo account.
- [ ] User roles and facility scoping are visible and enforced.

Evidence to capture: application dashboard, database health, migration head and API docs.

### B. Facility and inventory visibility

- [ ] Show at least three synthetic facilities on the network.
- [ ] Show the canonical product/medicine record.
- [ ] Show available, reserved and total stock distinctly.
- [ ] Show batch numbers, manufacture/expiry dates and eligible quantities.
- [ ] Show inventory freshness or last-updated timestamp if available.

Evidence: facility list/map, inventory view and batch details.

### C. External inventory integration

- [ ] Register one integration source for a demo facility.
- [ ] Create an explicit external-code-to-canonical-product mapping.
- [ ] Submit a valid batch-level inventory snapshot.
- [ ] Verify that inventory is updated.
- [ ] Replay the same event ID and payload; verify no second inventory update.
- [ ] Reuse the same event ID with changed payload; verify rejection.
- [ ] Submit an unmapped product code or stale timestamp; verify rejection.
- [ ] Show the integration event receipt.

Evidence: request/response in Swagger or API client, integration source page and event receipt.

Security note: keep integration keys out of browser code, screenshots, source control and logs.

### D. Shortage and stockout-risk analysis

- [ ] Show available stock and daily consumption input.
- [ ] Show projected stockout days and risk category.
- [ ] Show lead time and safety-stock assumptions.
- [ ] Show the explanation for the risk result.
- [ ] Show an insufficient-data case where consumption history/rate is unavailable.

Evidence: forecast screen and API response.

### E. Emergency donor discovery

- [ ] Create or open the demo emergency case.
- [ ] Retrieve eligible donor candidates.
- [ ] Show geographic distance, transferable quantity, donor buffer and score breakdown.
- [ ] Show the ineligible candidate excluded before ranking.
- [ ] Explain that distance is straight-line distance, not road travel time.
- [ ] Explain that the ranking score is a decision-support score, not an ML probability.

Evidence: emergency detail, map and donor comparison.

### F. Human-approved transfer lifecycle

- [ ] Create a transfer request from the emergency case.
- [ ] Approve a quantity within the eligible transferable amount.
- [ ] Verify that stock reservation/allocations are consistent.
- [ ] Assign a transport type and vehicle reference.
- [ ] Dispatch the approved transfer.
- [ ] Mark delivery.
- [ ] Verify inventory settlement and transfer state.
- [ ] Open the emergency timeline and show the persisted milestones.

Evidence: transfer detail before/after each state change and final timeline.

### G. Future category expansion (not part of today's live demo)

Category-specific onboarding, including Ayurvedic products, is deferred. Mention it only as future scope after the core conventional-medicine redistribution workflow is validated. Do not present this as an implemented module or spend live-demo time on it.

- Product category: conventional medicine / Ayurvedic product.
- Product identity and formulation fields appropriate to the category.
- Manufacturer/marketer and applicable licence/registration references.
- Batch/lot traceability and product-specific date fields where applicable.
- Storage/handling conditions as declared by authoritative product information.
- Supplier/retailer/dispensary facility type.
- Explicit separation of supply coordination from clinical substitution or treatment advice.

Do not claim regulatory compliance or clinical interchangeability from the presence of these fields alone.

## 4. Data model capabilities to demonstrate

### Operational PostgreSQL/PostGIS

- facilities and locations
- canonical products/medicines
- inventory and inventory batches
- integration sources and product-code mappings
- integration event receipts
- emergencies
- transfer requests and batch allocations
- dispatch records
- append-only emergency timeline events

### Data Engineering capabilities to build next

- immutable raw payload archive (MinIO locally; S3-compatible later)
- Bronze source-faithful ingestion records
- Silver canonical, validated and reconciled data
- Gold analytical facts and dimensions
- historical inventory snapshots and daily consumption facts
- pipeline-run and data-quality metrics

The current repository has an integration gateway and an architectural blueprint, but the full raw/Bronze/Silver/Gold pipeline is not yet implemented. Do not present the blueprint as an operational pipeline.

## 5. First-review acceptance criteria

| Area | Acceptance criterion |
|---|---|
| Startup | API, frontend and PostgreSQL/PostGIS start reproducibly |
| Migrations | Fresh disposable database reaches Alembic head without manual schema edits |
| Inventory | Demo stock and batch records display consistently |
| Integration | Valid snapshot updates inventory and creates a receipt |
| Idempotency | Identical replay causes no duplicate stock movement |
| Validation | Invalid mapping/stale snapshot is rejected without partial update |
| Forecast | Rule-based stockout calculation returns explainable output |
| Matching | Only eligible donors are ranked and score components are visible |
| Approval | Unauthorized user cannot approve transfer |
| Lifecycle | Request → approval → dispatch → delivery transitions are enforced |
| Settlement | Delivered quantity and inventory allocation reconcile |
| Audit | Timeline shows persisted lifecycle milestones |
| Data integrity | No expired or incompatible stock is recommended |
| Ayurvedic | Category extension is documented and not represented as clinically interchangeable |

## 6. Review dashboard metrics

Populate these from actual run results; do not invent numbers:

- number of synthetic facilities and products loaded
- number of inventory records ingested
- accepted / rejected / replayed integration events
- inventory snapshot freshness
- number of eligible and excluded donors
- emergency-to-first-recommendation time
- transfer approval-to-dispatch and dispatch-to-delivery time
- pipeline/test pass rate
- data reconciliation differences

## 7. Prioritized implementation backlog

### P0 — Must work before the first review

1. Verify local branch and working tree; preserve any uncommitted work.
2. Verify Docker/PostGIS health and environment configuration.
3. Test the entire Alembic chain on a disposable PostgreSQL/PostGIS database.
4. Prepare deterministic synthetic demo records and documented reset procedure.
5. Run the full emergency scenario through the UI/API.
6. Fix any broken transitions, data mismatches or access-control defects found.
7. Capture evidence and prepare a fallback API-driven demo.

### P1 — Strong first-review upgrades

1. Add inventory freshness indicators.
2. Improve integration event visibility and clear rejection reasons.
3. Show donor score breakdown and hard eligibility exclusions in the UI.
4. Show stockout assumptions and insufficient-data states.
5. Make the emergency timeline easy to inspect.
6. Add a reproducible demo setup guide and smoke tests.

### P2 — Next milestone, not a first-review blocker

1. Durable raw payload storage.
2. Implement Bronze/Silver/Gold processing.
3. Add historical inventory and consumption facts.
4. Build dbt transformations and quality tests.
5. Train/evaluate demand forecasting against a baseline.
6. Add category-aware Ayurvedic product onboarding.
7. Add Airflow orchestration after pipeline tasks are independently testable.

## 8. Demo fallback plan

If the frontend fails during the review:

1. Open FastAPI Swagger UI.
2. Authenticate and show the same API workflow.
3. Submit the valid synthetic inventory snapshot.
4. Show the resulting inventory and forecast.
5. Retrieve donor matches.
6. Request, approve, dispatch and deliver the transfer through the API.
7. Show the final timeline and database state.

The fallback must use the same demo dataset and application services; do not substitute screenshots for a claimed live operation.

## 9. Review presentation structure

1. Problem and motivation.
2. AegisFlow objective and stakeholders.
3. System architecture and operational/data lanes.
4. Live multi-facility inventory view.
5. Integration and data validation demonstration.
6. Stockout-risk calculation.
7. Explainable donor matching.
8. Emergency transfer approval and dispatch.
9. Deferred product-category expansion (future scope).
10. Implemented capabilities, current limitations and next milestone.

## 10. Definition of done

The first review milestone is ready when a fresh local environment can be started, synthetic data can be loaded through a documented process, and the team can reproduce the entire emergency workflow from inventory ingestion through delivery and audit without manually editing the database or bypassing application rules.
