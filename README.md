# AegisFlow

**An Interoperable Healthcare Supply Network Intelligence and Emergency Redistribution Platform**

AegisFlow connects existing healthcare systems for controlled availability sharing, predictive supply intelligence, policy-aware network coordination, and human-approved emergency redistribution. It is designed as an interoperability layer, not a replacement for hospital, pharmacy, or supplier systems.

1. Clone repository

2. Backend

cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

docker compose up -d

alembic upgrade head----()

python seed/seed_all.py

uvicorn app.main:app --reload

3. Frontend

cd frontend

npm install

copy .env.example .env

npm run dev