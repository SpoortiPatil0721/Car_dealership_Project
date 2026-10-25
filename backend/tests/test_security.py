from datetime import timedelta

import pytest

from app.config import Settings
from app.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.fixture
def settings():
    return Settings(jwt_secret="unit-test-secret-padded-out-to-32-bytes", password_iterations=1000)


def test_hashed_password_verifies(settings):
    hashed = hash_password("hunter22", settings)
    assert hashed != "hunter22"
    assert verify_password("hunter22", hashed)


def test_wrong_password_does_not_verify(settings):
    hashed = hash_password("hunter22", settings)
    assert not verify_password("hunter23", hashed)


def test_same_password_gets_different_salt(settings):
    assert hash_password("same-pass", settings) != hash_password("same-pass", settings)


def test_garbage_hash_never_verifies():
    assert not verify_password("anything", "not-a-real-hash")


def test_token_round_trip(settings):
    token = create_access_token(user_id=7, is_admin=True, settings=settings)
    claims = decode_access_token(token, settings)
    assert claims["sub"] == "7"
    assert claims["admin"] is True


def test_expired_token_is_rejected(settings):
    token = create_access_token(user_id=1, is_admin=False, settings=settings, expires_in=timedelta(seconds=-5))
    with pytest.raises(InvalidTokenError):
        decode_access_token(token, settings)


def test_token_signed_with_other_secret_is_rejected(settings):
    other = Settings(jwt_secret="someone-else-with-a-different-long-secret")
    token = create_access_token(user_id=1, is_admin=False, settings=other)
    with pytest.raises(InvalidTokenError):
        decode_access_token(token, settings)
