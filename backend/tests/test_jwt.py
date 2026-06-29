from app.core.jwt import create_access_token
from app.core.jwt import decode_token


def test_token_creation():
    token = create_access_token(
        subject="user123",
        role="USER",
    )

    assert token is not None
    assert isinstance(token, str)


def test_token_decoding():
    token = create_access_token(
        subject="user123",
        role="USER",
    )

    payload = decode_token(token)

    assert payload["sub"] == "user123"
    assert payload["role"] == "USER"