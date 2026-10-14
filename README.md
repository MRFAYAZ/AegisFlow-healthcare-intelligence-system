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