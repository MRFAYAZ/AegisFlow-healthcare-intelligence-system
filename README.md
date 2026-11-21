# AegisFlow

**Healthcare Supply-Network Intelligence and Emergency Redistribution Prototype**

AegisFlow is a multi-facility coordination platform that helps participating healthcare facilities share limited, authorized inventory information, identify potential stockout risks, discover eligible donor facilities, and coordinate human-approved emergency transfers.

It is designed to complement—not replace—each participant's existing HIS, ERP, pharmacy POS or inventory system.

## Project goals

- Integrate facility inventory through authenticated APIs and explicit medicine-code mappings.
- Maintain batch-aware inventory and protect against expired or ineligible stock.
- Estimate stockout risk using transparent, explainable calculations.
- Rank eligible donor facilities using distance, transferable quantity and donor stock protection.
- Coordinate transfer request, approval, dispatch and delivery with an auditable timeline.
- Build a historical data foundation for demand forecasting and network analytics.
- Extend the product catalogue to conventional and Ayurvedic medicine products using category-appropriate metadata and validation.

## Current technology

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | Python, FastAPI, Pydantic |
| Operational database | PostgreSQL |
| Geospatial queries | PostGIS, GeoAlchemy |
| Persistence and migrations | SQLAlchemy, Alembic |
| Map and charts | Leaflet, Recharts |
| Local database environment | Docker Compose |

## Intelligence approach

AegisFlow currently uses deterministic, explainable decision-support logic:

1. **Donor ranking:** weighted scoring of geographic distance, transferable quantity and donor stock buffer, after hard eligibility checks.
2. **Stockout projection:** a rule-based calculation using usable stock, daily consumption, replenishment lead time and safety-stock days.

These are not trained machine-learning models and their scores are not probabilities. A future demand-forecasting model will be trained only after sufficient historical consumption data is captured and evaluated against a baseline. RAG and vector search are not required for the current core workflow.

## Current operational workflow

1. A facility or external inventory system supplies a batch-level inventory snapshot.
2. The integration gateway authenticates the source, validates its contract, mappings and timestamp, and handles idempotent replays.
3. AegisFlow updates operational inventory and batch records transactionally.
4. A shortage/emergency is reviewed and eligible donor facilities are ranked.
5. A human operator requests a transfer; an authorized user approves or rejects it.
6. Transport is assigned, the shipment is dispatched, and delivery is confirmed.
7. Operational events are available through the emergency timeline.

## Repository structure

```text
backend/
  app/
    api/             FastAPI routes
    engines/         Matching, safety and stockout calculations
    models/          SQLAlchemy data models
    schemas/         Pydantic request/response contracts
    services/        Business workflows and integration services
  alembic/           Versioned database migrations
  tests/             Automated backend tests
  etl/               Planned data-pipeline modules
frontend/
  src/pages/         React application screens
docs/
  DATA_ENGINEERING_BLUEPRINT.md
  EXTERNAL_INTEGRATION.md
  FIRST_REVIEW_DEMO.md
```

## Local setup

### Prerequisites

- Python 3.12
- Node.js 22 and npm
- Docker Desktop / Docker Engine with Compose
- PostgreSQL/PostGIS through the provided Compose service

### 1. Configure environment

Create a local `.env` file using the variables required by the backend configuration. Never commit real credentials or secret keys.

### 2. Start PostgreSQL/PostGIS

```bash
docker compose up -d postgres
docker compose ps
```

The database service uses `postgis/postgis:16-3.4`. Confirm the configured database name, username and password in your local environment before connecting.

### 3. Install backend dependencies

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 4. Apply database migrations

From the repository root, use the backend Alembic configuration and verify the target database URL before running migrations:

```bash
cd backend
alembic upgrade head
cd ..
```

Do not run migrations against a database containing important data without a verified backup. For review preparation, first validate the migration chain against a disposable local database.

### 5. Start the API

From the repository root:

```bash
cd backend
uvicorn app.main:app --reload
```

Open the FastAPI documentation at `http://127.0.0.1:8000/docs` if the configured API host and port are the defaults.

### 6. Start the frontend

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

Use the Vite URL printed in the terminal. API base URL and CORS settings must match the local backend configuration.

## Testing

Backend tests used by the current zeroth-review workflow:

```bash
PYTHONPATH=backend pytest -q \
  backend/tests/test_geospatial_matching.py \
  backend/tests/test_transfer_state_machine.py \
  backend/tests/test_forecast_engine.py \
  backend/tests/test_medicine_safety.py \
  backend/tests/test_integration_contract.py
python -m compileall -q backend/app backend/tests
```

Frontend type-check and production build:

```bash
cd frontend
npm ci
npm run build
```

Passing these checks does not prove that migrations work against a live PostgreSQL instance or that every frontend workflow has been tested end to end. See the first-review runbook for the demonstration acceptance checklist.

## Documentation

- [Data Engineering Blueprint](docs/DATA_ENGINEERING_BLUEPRINT.md)
- [External Inventory Integration Contract](docs/EXTERNAL_INTEGRATION.md)
- [First Review Demo Runbook](docs/FIRST_REVIEW_DEMO.md)

## Scope and limitations

- Donor distance is a geographic straight-line estimate, not a road route or guaranteed travel time.
- Stockout projection is rule-based; historical ML forecasting is future work.
- Registering an integration source does not install a real partner HIS/ERP/POS adapter.
- Facility cold-chain capability is currently a declared attribute, not live temperature telemetry.
- Ayurvedic product onboarding and category-specific validation require further implementation and domain review.
- The prototype supports supply coordination and traceability; it does not prescribe treatment, establish clinical equivalence, or recommend substituting one medicine system for another.
- Production deployment requires security review, operational monitoring, backup/recovery procedures, partner validation and compliance review.

## Development status

This repository is under active academic prototype development. Features should be described as implemented only when verified in the running application and supported by tests. Synthetic demonstration records must be labelled as synthetic.
