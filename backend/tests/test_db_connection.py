from app.core.database import SessionLocal


def test_db_connection():
    db = SessionLocal()

    try:
        print("✅ Database session created successfully")

    finally:
        db.close()


if __name__ == "__main__":
    test_db_connection()