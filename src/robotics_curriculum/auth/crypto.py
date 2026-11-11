"""Passwords (Argon2id) and opaque tokens (random, stored as SHA-256)."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

MIN_PASSWORD = 12
MAX_PASSWORD = 128

# docs/architecture/auth.md §2.1: time_cost=3, memory_cost=64 MiB, parallelism=4.
_HASHER = PasswordHasher(time_cost=3, memory_cost=64 * 1024, parallelism=4)


class PasswordPolicyError(ValueError):
    """The password does not meet the policy."""


class Passwords:
    """Argon2id hashing with an optional server-side pepper appended to the password."""

    def __init__(self, pepper: str = "", hasher: PasswordHasher = _HASHER) -> None:
        self._pepper = pepper
        self._hasher = hasher
        # Verified against when the account does not exist, so both paths cost the same.
        self._dummy = hasher.hash(secrets.token_urlsafe(16))

    def hash(self, password: str) -> str:
        return self._hasher.hash(password + self._pepper)

    def verify(self, stored: str | None, password: str) -> bool:
        """Constant-ish time: an unknown account still pays for one Argon2 verification."""
        try:
            return self._hasher.verify(stored or self._dummy, password + self._pepper) and (
                stored is not None
            )
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def needs_rehash(self, stored: str) -> bool:
        return self._hasher.check_needs_rehash(stored)


def check_policy(password: str, *, email: str, display_name: str | None = None) -> None:
    """12-128 characters, not containing the email's local part or the display name."""
    if len(password) < MIN_PASSWORD:
        raise PasswordPolicyError(f"password must be at least {MIN_PASSWORD} characters")
    if len(password) > MAX_PASSWORD:
        raise PasswordPolicyError(f"password must be at most {MAX_PASSWORD} characters")
    lowered = password.lower()
    local = email.split("@", 1)[0].lower()
    if len(local) >= 3 and local in lowered:
        raise PasswordPolicyError("password must not contain your email address")
    if display_name and len(display_name) >= 3 and display_name.lower() in lowered:
        raise PasswordPolicyError("password must not contain your name")


def new_token(prefix: str = "") -> str:
    """256 random bits, URL-safe."""
    return prefix + secrets.token_urlsafe(32)


def token_hash(token: str) -> str:
    """What the database stores for a token (SHA-256 hex)."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def same(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
