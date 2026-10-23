import hashlib
import secrets
import sqlite3


PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_MIN_LENGTH = 12
PASSWORD_SALT_LENGTH = 16
PASSWORD_HASH_LENGTH = 32
_DUMMY_SALT = bytes(PASSWORD_SALT_LENGTH)
_DUMMY_HASH = bytes(PASSWORD_HASH_LENGTH)


def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
        dklen=PASSWORD_HASH_LENGTH,
    )


def create_user(
    connection: sqlite3.Connection, username: str, password: str
) -> None:
    username = username.strip()
    if not username or len(username) > 100:
        raise ValueError("Username must be between 1 and 100 characters")
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
        )

    salt = secrets.token_bytes(PASSWORD_SALT_LENGTH)
    password_hash = _hash_password(password, salt)
    connection.execute(
        """
        INSERT INTO users (username, password_salt, password_hash)
        VALUES (?, ?, ?)
        """,
        (username, salt, password_hash),
    )
    connection.commit()


def verify_user_credentials(
    connection: sqlite3.Connection, username: str, password: str
) -> bool:
    row = connection.execute(
        "SELECT password_salt, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    salt = row[0] if row is not None else _DUMMY_SALT
    expected_hash = row[1] if row is not None else _DUMMY_HASH
    actual_hash = _hash_password(password, salt)
    return secrets.compare_digest(actual_hash, expected_hash) and row is not None
