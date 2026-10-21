# AegisFlow — Data Engineering Blueprint

**Goal:** evolve AegisFlow from a healthcare supply operations application into a demonstrable, end-to-end Data Engineering platform that ingests multi-organization inventory signals, makes the data trustworthy, models it for analytics, and feeds timely decisions back to operational users.

**Scope rule:** AegisFlow coordinates supply intelligence; it does not replace a hospital's HIS/ERP/POS, billing or patient-management system. Do not ingest patient-level records for this supply-chain use case.

---

## 1. The end-to-end architecture

```text
  EXTERNAL SOURCE SYSTEMS (data owners retain their systems)
  Hospital HIS / ERP / Pharmacy POS / Supplier ERP / Warehouse
              | REST snapshot or webhook | CSV/SFTP batch
              v
  ┌───────────────────────────────────────────────────────┐
  │ 1. INGESTION GATEWAY                                  │
  │ FastAPI · source-scoped credentials · schema contract │
  │ source_id · event_id · source_timestamp · medicine map│
  └─────────────────────────┬─────────────────────────────┘
                            │
               validate identity + contract
                            v
  ┌───────────────────────────────────────────────────────┐
  │ 2. IMMUTABLE RAW LANDING (to build)                   │
  │ MinIO locally / S3 in cloud · JSON/CSV/Parquet        │
  │ Keep original payload + source + received_at + hash  │
  └─────────────────────────┬─────────────────────────────┘
                            │ batch / scheduled processing
                            v
  ┌───────────────────────────────────────────────────────┐
  │ 3. BRONZE — source-faithful records (to build)        │
  │ append-only ingestion receipts · schema version      │
  │ deduplication key · ingestion status                  │
  └─────────────────────────┬─────────────────────────────┘
                            │ standardize / validate / reconcile
                            v
  ┌───────────────────────────────────────────────────────┐
  │ 4. SILVER — trusted canonical data (to build)         │
  │ facility + medicine mappings · UTC timestamps        │
  │ batch/expiry checks · units · dedupe · quarantine     │
  │ stock/reservation reconciliation · data quality      │
  └─────────────────────────┬─────────────────────────────┘
                            │ incremental transformations
                            v
  ┌───────────────────────────────────────────────────────┐
  │ 5. GOLD — analytics warehouse / marts (to build)     │
  │ dim_date · dim_facility · dim_medicine · dim_geo      │
  │ fact_inventory_snapshot · fact_consumption            │
  │ fact_shortage · fact_emergency · fact_transfer        │
  │ fact_pipeline_run · fact_integration_event             │
  └─────────────────────────┬─────────────────────────────┘
                            │
                 SQL marts / API / BI
                            v
  ┌───────────────────────────────────────────────────────┐
  │ 6. DATA PRODUCTS                                      │
  │ stockout risk · regional shortage index · demand trend│
  │ donor capacity · emergency response SLA · data health │
  └─────────────────────────┬─────────────────────────────┘
                            │ decision support, not auto-approval
                            v
  AegisFlow EOC / Hospital Admin / Donor Ops / Command Dashboard


  OPERATIONAL LANE (separate from analytics)

  Validated source snapshot -> PostgreSQL/PostGIS operational DB
     -> current inventory + batch lots + emergency/transfer state
     -> human approval -> transport assignment -> dispatch/delivery
     -> transactional inventory settlement + append-only timeline

  The analytics warehouse never approves a transfer or writes live
  operational stock. Live operational workflow remains authoritative.
```

### Two lanes are deliberate

- **Operational lane:** supports correct live state and transactional work. PostgreSQL/PostGIS and the FastAPI services remain authoritative for inventory, transfer approvals, dispatch, delivery and emergency status.
- **Analytical lane:** extracts changes and historical snapshots into a separate analytical model. It is optimized for trends, regional risk, forecasting evaluation, response time and network planning. A reporting query must not slow or mutate a live emergency workflow.

For a student-scale deployment, the operational database and warehouse can be separate databases on the same local PostgreSQL server. Production should isolate workload, access and backups; a cloud warehouse/object store can be adopted later.

---

## 2. Proposed technology stack

| Concern | Primary choice | Why it belongs in the project |
|---|---|---|
| Source integration | FastAPI REST + CSV batch adapter | Real systems can publish snapshots without migrating to AegisFlow |
| Validation/contracts | Pydantic + explicit business rules | Reject malformed, stale, unmapped or contradictory records at the boundary |
| Operational database | PostgreSQL + PostGIS | Transactional inventory, transfer state and geospatial matching |
| Database access/migrations | SQLAlchemy + Alembic | Typed persistence and reproducible schema changes |
| Raw data storage | MinIO locally; S3-compatible cloud storage later | Retain source payloads for replay, debugging and audit |
| File format | JSON for original partner payload; Parquet for curated history | JSON preserves payload shape; Parquet is efficient for analytical datasets |
| Pipeline language | Python | Ingestion adapters, reconciliation, quality rules and job orchestration |
| Transformations | SQL + dbt Core | Versioned staging/intermediate/mart models with dependency graph and tests |
| Orchestration | Apache Airflow | Schedule, retry, backfill and monitor a multi-step batch pipeline |
| Analytics store | PostgreSQL warehouse initially | Easier local development; can migrate to a cloud warehouse after volume justifies it |
| Data quality | Pydantic contracts + SQL/dbt tests + pytest | Tests schema, keys, freshness, reconciliation and business invariants |
| Application APIs/UI | Existing FastAPI + React/TypeScript | Exposes operational actions and analytical data products |
| Containerization | Docker Compose | Reproducible local environment for app, database, object store and orchestration |
| CI | GitHub Actions | Run unit tests, integration-contract tests, Python compilation and frontend build |
| Observability | Structured logs + pipeline-run table first; metrics/alerts later | Make failures, lag and quality drift visible |
| BI | SQL views + Metabase or Power BI later | Demonstrate data products without building every chart from scratch |

**Do not add Kafka or Spark first.** For the current scale, API/webhook ingestion plus scheduled incremental batch processing is enough to demonstrate production-minded engineering. Kafka/CDC becomes worthwhile if event volume and latency needs justify it; Spark becomes worthwhile when data size/transform cost demands distributed compute. The blueprint leaves both as extension points rather than adding operational complexity before it is needed.

---

## 3. Data contract at the source boundary

Every source event should identify the data owner and the source's view of time.

Minimum envelope:
- `source_id`: registered integration source tied to one facility.
- `external_event_id`: stable idempotency key supplied by that source.
- `source_timestamp`: timezone-aware time when the source snapshot was valid.
- `received_at`: AegisFlow receipt time.
- `schema_version`: contract version used to validate this payload.
- `payload_hash`: canonical content hash to detect event-ID reuse with changed content.
- `items[]`: external medicine code, quantities, consumption/lead-time values and batch/expiry details.

Data-contract rules:
1. A medicine code must map explicitly to a canonical AegisFlow medicine; never silently fuzzy-match critical stock.
2. Quantity values must be non-negative and internally reconcilable.
3. Non-zero stock supplied for emergency redistribution needs batch/expiry traceability.
4. Cold-chain requirements are hard eligibility constraints, not ranking bonuses.
5. Duplicate `(source_id, external_event_id)` with identical content is a no-op; the same key with different content is rejected.
6. Older source snapshots must not overwrite a newer accepted snapshot.
7. Invalid records must be rejected or quarantined with a reason, not silently discarded.
8. Network sharing should expose only minimum stock/safety/location attributes needed for coordination; do not share customer or patient PII.

Current repository already has a source-scoped integration key, external medicine mappings, event receipts, timestamp/replay contract code and batch-level snapshot validation. The next data-platform step is to retain the immutable raw payload and process it through the explicit Bronze/Silver/Gold pipeline.

---

## 4. Lakehouse layers and transformations

### Raw landing / Bronze

**Purpose:** answer “what exactly did the partner send us?”

- Store the original JSON or CSV unchanged.
- Add source ID, event ID, received timestamp, payload hash, schema version and ingestion status.
- Partition storage by source and received date, e.g. `raw/source_id=.../received_date=YYYY-MM-DD/`.
- Write the object before marking an event accepted; store the object URI in the receipt.
- Retain rejected payloads subject to an approved retention policy, with sensitive fields minimized/redacted.
- Never overwrite a previous raw snapshot. Reprocessing should reference the original object and an explicit pipeline version.

### Silver / canonical data

**Purpose:** answer “what does this record mean in AegisFlow's data model?”

- Standardize medicine codes through explicit mapping tables.
- Normalize timestamps to UTC; preserve source timestamp separately.
- Reconcile total stock, available, reserved, and batch quantities.
- Validate batch identity, manufacturing/expiry dates and duplicates.
- Apply event idempotency and stale-snapshot rules.
- Track data-quality outcomes and quarantine rows that fail non-fatal checks.
- Preserve source and ingestion lineage columns on standardized rows.

### Gold / data marts

**Purpose:** provide analytics at a defined, tested grain.

| Mart / fact | Grain (one row represents…) | Main questions answered |
|---|---|---|
| `fact_inventory_snapshot` | one facility × medicine × snapshot time | How did usable stock and risk change over time? |
| `fact_consumption_daily` | one facility × medicine × calendar date | What is daily/weekly demand and how seasonal is it? |
| `fact_shortage_event` | one shortage/risk event | Which shortages recur, how severe are they and for how long? |
| `fact_emergency` | one emergency case | How quickly are emergencies sourced and resolved? |
| `fact_transfer_leg` | one donor-to-recipient transfer | What quantity was requested, approved, dispatched and delivered? |
| `fact_pipeline_run` | one pipeline execution | Which run failed, how long did it take, how many rows changed? |
| `fact_integration_event` | one source event | Which sources are fresh, stale, failing or repeatedly replaying? |

Dimensions:
- `dim_date`: date, day, week, month, quarter, year and season where justified.
- `dim_facility`: facility type and geography. Use slowly changing history (SCD2) for meaningful changes to classification/region.
- `dim_medicine`: canonical medicine category, dosage form, strength and cold-chain class. Track changes explicitly when historical comparisons require it.
- `dim_geography`: city/district/state/region roll-ups.
- `dim_source_system`: partner type, source identifier and integration metadata.

**Modeling rule:** define and document each fact's grain before writing SQL. Do not build a “wide report table” that accidentally multiplies quantities when transfers, batches and emergencies join one-to-many.

---

## 5. The scheduled pipeline (first full Data Engineering milestone)

Create one orchestrated pipeline that runs on a schedule and can be rerun safely.

```text
extract_changed_records
  -> archive_raw_payload_or_extract
  -> load_bronze
  -> validate_contract_and_freshness
  -> standardize_to_silver
  -> run_data_quality_tests
  -> update_gold_marts_incrementally
  -> publish_pipeline_metrics
  -> notify_on_failure_or_bad_quality
```

### Incremental-load contract

- Prefer a source event log/outbox or an `updated_at` + stable primary key cursor.
- Persist the last successful cursor only after all required target writes and checks succeed.
- Overlap a small time window where needed, then deduplicate by stable key.
- Upsert using deterministic unique keys. Re-running the same source window should produce the same target state.
- Failed records go to a quarantine table/object path with a reason and replay reference.
- Backfills take an explicit date/source range and run ID; they must not duplicate facts.
- Reconciliation compares source and target counts/quantities by source, facility, medicine, batch and snapshot time.

Airflow DAG tasks should use separate functions/modules so the same logic is unit-testable outside Airflow. Initial cadence can be every 15 minutes for the demo; state the actual freshness SLA and measure it rather than calling the pipeline “real time.”

---

## 6. Data quality and operational reliability

Run these checks at ingestion and again where appropriate in Silver/Gold.

**Schema:** required fields, types, allowed enums, schema version.

**Keys/deduplication:** no duplicate batch number within a snapshot; no duplicate fact grain; one canonical mapping per source/external medicine key.

**Validity:** non-negative quantities, valid coordinates, expiry not before manufacture, timezone-aware timestamps, nonzero stock has batches.

**Reconciliation:**
- source inventory totals equal the aggregate of batch quantities under the declared quantity contract;
- AegisFlow reservations are preserved across incoming source snapshots;
- Silver counts/quantities reconcile to accepted Bronze records;
- Gold transfer quantities reconcile to operational transfer records.

**Freshness:** time since each facility's most recent accepted snapshot, time since last successful pipeline run and source-to-warehouse lag.

**Business rules:** expired inventory is never eligible for donor recommendations; donor safety threshold is protected; a cold-chain medicine cannot be matched or assigned to an incompatible facility/vehicle; delivery is not counted twice.

**Quarantine:** store source/event/batch identifiers, rule name, failed value or safe summary, failure timestamp and resolution status. Do not dump secret keys or patient/customer information into logs.

---

## 7. Metrics and dashboards that prove the data pipeline works

### Data platform dashboard
- ingestion events accepted/rejected/replayed
- freshness by source/facility
- source-to-warehouse lag (p50/p95)
- rows read, accepted, changed, rejected and quarantined
- reconciliation differences by source and run
- pipeline success rate and duration
- last successful watermark and last failure
- duplicate events prevented
- unknown medicine mappings
- batch/expiry data coverage

### Supply-intelligence business dashboard
- inventory availability and days-to-stockout by medicine/region
- recurring shortage frequency and duration
- emergency time-to-first-eligible-donor
- emergency time-to-hospital-decision
- time from approval to dispatch and dispatch to delivery
- requested vs approved vs fulfilled quantities
- partial vs complete emergency fulfillment
- donor network capacity and concentration risk

For every metric, document the numerator, denominator, grain, time zone, excluded statuses and refresh cadence. A score/number is not a useful data product if its definition changes from chart to chart.

---

## 8. Testing strategy

1. **Unit tests:** parsers, mapping rules, timestamp handling, FEFO batch safety, stockout projection and scoring boundaries.
2. **Contract tests:** valid/invalid snapshots, missing columns, unknown medicine code, malformed batch, duplicate event ID with identical/different content, stale source timestamp.
3. **Transformation tests:** unique fact grain, accepted enum values, no negative measures, complete date/facility/medicine keys.
4. **Reconciliation tests:** inventory and batch totals agree, internal transfer reservations survive source refresh, warehouse quantities reconcile to operational records.
5. **Idempotency tests:** run the same input twice and assert that neither operational inventory nor warehouse measures double-count.
6. **Failure/recovery tests:** inject a failure between pipeline stages, rerun from a recorded cursor, and show that completed stages do not cause duplicates.
7. **End-to-end demo:** ingest a partner snapshot, validate and archive it, process it through Silver/Gold, show the mart result, create an emergency recommendation, and verify that analytics reflect the recorded transfer events.

Keep synthetic test datasets reproducible and explicitly label them as synthetic. Do not invent real hospital adoption or partner integrations.

---

## 9. Recommended repository layout

```text
AegisFlow/
  backend/
    app/
      api/routes/integrations.py
      engines/integration/
      services/integration_service.py
      engines/inventory/
      services/...
    etl/
      extract_operational.py
      archive_raw.py
      load_bronze.py
      transform_silver.py
      publish_gold.py
      quality_checks.py
      reconcile.py
    tests/
      unit/
      contracts/
      integration/
      end_to_end/
    database/
      schema/
      validation/
  data-platform/
    airflow/dags/aegisflow_supply_pipeline.py
    dbt/
      dbt_project.yml
      models/staging/
      models/intermediate/
      models/marts/
      tests/
    samples/
      valid/
      invalid/
    docs/
  infra/
    docker-compose.yml
  docs/
    DATA_ENGINEERING_BLUEPRINT.md
    DATA_DICTIONARY.md
    SOURCE_CONTRACTS.md
    RUNBOOK.md
```

Treat this as the target structure, not a claim that all files already exist. Do not commit `venv/`, `__pycache__/`, secrets, real partner data or generated output files.

---

## 10. Delivery roadmap — build one thin vertical slice first

### Phase 0 — baseline and repository hygiene
- Confirm branch/DB migration head and current CI.
- Remove virtual environments and bytecode from Git tracking; add/update `.gitignore`.
- Document existing tables and exact source-of-truth boundaries.
- Capture a reproducible baseline dataset and test command.

### Phase 1 — first end-to-end source pipeline (highest priority)
- Finalize versioned partner snapshot contract.
- Add immutable raw payload storage in MinIO/S3 and a raw-object URI in the ingestion receipt.
- Build one CSV adapter plus existing API snapshot source.
- Implement Bronze → Silver normalization, explicit quarantine and reconciliation.
- Prove source event replays do not change counts or stock twice.

**Acceptance:** one valid snapshot travels from source through raw/Bronze/Silver to operational PostgreSQL with a recorded run ID; one invalid snapshot is quarantined with an actionable reason; a replay is a no-op.

### Phase 2 — orchestrate and observe
- Add Airflow DAG, retries, timeouts, backfill parameters and stored run metrics.
- Add freshness/quality dashboard and failure notification.
- Demonstrate a deliberate failure and clean recovery.

**Acceptance:** a fresh environment can run the pipeline using documented commands; last successful cursor advances only after validations pass.

### Phase 3 — analytics warehouse
- Create separate warehouse schema/database and versioned migrations.
- Add dbt staging, intermediate and mart models.
- Build inventory snapshot, daily consumption, shortages, emergency and transfer facts.
- Add dbt tests and reconciliation from operational records.

**Acceptance:** reruns are idempotent; a business KPI can be traced from chart → Gold SQL → Silver rows → original source event.

### Phase 4 — predictive intelligence backed by history
- Establish a reliable daily consumption history from accepted snapshots and trustworthy consumption events.
- Build a baseline forecast, backtest on a time-based holdout, and measure MAE/WAPE and stockout-warning precision/recall.
- Compare current deterministic stockout rules with a statistical model only after enough valid history exists.
- Version model/features/results and expose freshness/limitations.

**Acceptance:** report evaluation data, baseline, metrics and limitations; never call a deterministic rule or a score a trained AI model.

### Phase 5 — network scale / cloud
- Add CDC/event streaming only if volume and latency require it.
- Consider object-store lakehouse tables or a managed warehouse when needed.
- Add centralized secrets, alerting, RBAC audits, retention policies, backups and recovery exercises.
- Integrate a real pilot partner only with explicit permissions and tested contracts.

---

## 11. Definition of “complete Data Engineering project” for a portfolio

AegisFlow becomes a strong end-to-end DE project when the repository proves all of the following:

- Multiple sources can be ingested through stable, versioned contracts.
- Raw input is preserved and every record/run has traceable lineage.
- Data is validated, normalized, deduplicated and quarantined where appropriate.
- Loads are incremental, idempotent, retryable and backfillable.
- There is an orchestrated DAG with observable dependencies and failure recovery.
- A dimensional warehouse supports tested analytics with documented fact grains.
- Data-quality/reconciliation tests run in CI and in the pipeline.
- Dashboards measure data freshness/reliability as well as healthcare supply outcomes.
- A historical dataset evaluates a forecast against a simple baseline.
- One command sequence rebuilds the demo from a fresh development environment.
- The README includes architecture, ERD/data dictionary, run commands, tests, sample source payloads, pipeline screenshots and measured results.

**Current-state assessment from repository inspection:** AegisFlow already has the operational PostgreSQL/PostGIS domain, FastAPI integration endpoints/contracts, canonical medicine mappings, integration-event/idempotency records, inventory batches, deterministic shortage-risk logic, analytics service code, a draft star-schema SQL file, and CI tests. The files `backend/etl/ingest.py`, `clean.py`, `score.py` and `load.py` are currently empty. No configured Airflow DAG, dbt project, immutable object-store landing, or completed automated Bronze/Silver/Gold pipeline was found in the inspected tree. Those missing pieces—not adding more UI pages—are the highest-value work to prove the Data Engineering claim.
