from app.core.security import Permission, Role, create_access_token, decode_access_token, hash_password, verify_password


def test_password_hashing_round_trip():
    hashed = hash_password("StrongPassword123")

    assert hashed != "StrongPassword123"
    assert verify_password("StrongPassword123", hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_jwt_round_trip():
    token = create_access_token(
        subject="user-1",
        claims={
            "role": Role.INVESTIGATOR.value,
            "permissions": [Permission.READ_CASES.value],
        },
    )

    payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["role"] == Role.INVESTIGATOR.value
    assert payload["permissions"] == [Permission.READ_CASES.value]
