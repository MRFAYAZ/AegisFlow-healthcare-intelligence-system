from app.core.database import SessionLocal

from sqlalchemy import text


def test_database_health():

    db = SessionLocal()

    try:

        result = db.execute(
            text(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname='public'
                """
            )
        )

        tables = [

            row[0]

            for row in result.fetchall()

        ]

        print("\nDATABASE TABLES:\n")

        for table in tables:

            print(table)

        print(
            "\n✅ Database healthy"
        )

    finally:

        db.close()


if __name__ == "__main__":

    test_database_health()