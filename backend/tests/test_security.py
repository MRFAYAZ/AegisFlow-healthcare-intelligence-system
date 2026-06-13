from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)


def test_security():

    password = "aegisflow123"

    hashed = hash_password(password)

    verified = verify_password(
        password,
        hashed
    )

    token = create_access_token({
        "sub": "test_user"
    })

    print("HASH:", hashed)

    print("VERIFIED:", verified)

    print("TOKEN:", token)

    print("✅ Security layer working")


if __name__ == "__main__":
    test_security()