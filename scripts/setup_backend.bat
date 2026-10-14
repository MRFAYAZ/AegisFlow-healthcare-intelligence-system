python -m venv venv

call venv\Scripts\activate

pip install -r requirements.txt

copy .env.example .env

echo Backend setup completed.