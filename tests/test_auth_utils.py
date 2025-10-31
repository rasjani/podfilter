"""
Unit tests for the authentication utility helpers.
"""

from datetime import timedelta

import pytest

from podfilter import auth


def test_hash_password_and_verify_roundtrip() -> None:
  """Hashing and verification should succeed for the original password."""
  hashed = auth.hash_password("super-secret")

  assert hashed != "super-secret"
  assert auth.verify_password("super-secret", hashed)


def test_verify_password_rejects_invalid_input() -> None:
  """Verifying with the wrong password should fail."""
  hashed = auth.hash_password("correct-horse")

  assert not auth.verify_password("wrong-battery", hashed)


def test_create_and_verify_access_token(monkeypatch: pytest.MonkeyPatch) -> None:
  """Tokens should round-trip when using the same secret key."""
  monkeypatch.setattr(auth, "SECRET_KEY", "unit-test-secret", raising=False)
  token = auth.create_access_token({"sub": "alice"}, expires_delta=timedelta(minutes=5))

  assert auth.verify_token(token) == "alice"


def test_verify_token_returns_none_for_invalid_secret(monkeypatch: pytest.MonkeyPatch) -> None:
  """Tokens signed with a different secret should not validate."""
  monkeypatch.setattr(auth, "SECRET_KEY", "unit-test-secret", raising=False)
  token = auth.create_access_token({"sub": "bob"}, expires_delta=timedelta(minutes=5))

  monkeypatch.setattr(auth, "SECRET_KEY", "another-secret", raising=False)

  assert auth.verify_token(token) is None
