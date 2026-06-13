from app.core.security import verify_password

hash_value = "$2b$12$.ZkH/Os/w9oH24HZcHpsjuRaBBQ8sAaeli5c2lWUsLyxT2MXsqxJi"

print(
    verify_password(
        "admin123",
        hash_value
    )
)