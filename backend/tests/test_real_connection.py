from sqlalchemy import text

from app.core.database import SessionLocal


db = SessionLocal()

try:
    result = db.execute(
        text("SELECT version();")
    )

    print(result.fetchone())

    print("✅ Real DB connection successful")

finally:
    db.close()