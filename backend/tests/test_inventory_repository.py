from app.core.database import SessionLocal

from app.repositories.inventory_repository import (
    InventoryRepository
)


def test_inventory_repository():

    db = SessionLocal()

    try:

        repo = InventoryRepository(db)

        result = repo.get_low_stock_inventory()

        print(result)

        print("✅ Repository working successfully")

    finally:
        db.close()


if __name__ == "__main__":
    test_inventory_repository()