from app.core.config import settings


def test_config():
    print("✅ Project:", settings.PROJECT_NAME)

    print("✅ Database URL:", settings.DATABASE_URL)

    print("✅ JWT Algorithm:", settings.JWT_ALGORITHM)


if __name__ == "__main__":
    test_config()