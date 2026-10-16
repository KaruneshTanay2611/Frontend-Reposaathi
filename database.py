"""
RepoSathi Database & Authentication Module
Provides SQLite database persistence, bcrypt password hashing,
input validation, and user session management.
"""

import os
import re
import sqlite3
from typing import Dict, List, Optional, Tuple
import bcrypt

# Database file path in project directory
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reposathi.db")

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def get_db_connection() -> sqlite3.Connection:
    """Create and return a thread-safe connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize database tables using parameterized idempotent schemas."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # User-Scoped Saved Repositories Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_saved_repos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                repo_name TEXT NOT NULL,
                saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE(user_id, repo_name)
            );
        """)
        conn.commit()


# ==============================================================================
# PASSWORD SECURITY & VALIDATION
# ==============================================================================

def validate_email(email: str) -> bool:
    """Validate standard email format."""
    if not email or len(email.strip()) > 254:
        return False
    return bool(EMAIL_REGEX.match(email.strip()))


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password requirements:
    - At least 8 characters long
    - Contains at least one letter
    - Contains at least one digit or special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[a-zA-Z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one digit or special character."
    return True, ""


def hash_password(plain_password: str) -> str:
    """Hash password securely using bcrypt with automatic salt generation."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


# ==============================================================================
# USER REGISTRATION & AUTHENTICATION
# ==============================================================================

def register_user(full_name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
    """
    Register a new user with input validation, duplicate rejection,
    and bcrypt hashing.
    """
    clean_name = full_name.strip()
    clean_email = email.strip().lower()

    if not clean_name:
        return False, "Please provide your full name."
    if not validate_email(clean_email):
        return False, "Please enter a valid email address (e.g. name@example.com)."
    if password != confirm_password:
        return False, "Passwords do not match."

    pw_ok, pw_err = validate_password_strength(password)
    if not pw_ok:
        return False, pw_err

    pw_hash = hash_password(password)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?);",
                (clean_name, clean_email, pw_hash)
            )
            conn.commit()
            return True, "Account created successfully! You can now log in."
    except sqlite3.IntegrityError:
        return False, "An account with this email address already exists."
    except Exception as err:
        return False, f"Database error during registration: {str(err)}"


def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
    """
    Authenticate user using email and password.
    Returns generic error to prevent account enumeration.
    """
    clean_email = email.strip().lower()
    if not clean_email or not password:
        return False, None, "Please provide both email and password."

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, full_name, email, password_hash FROM users WHERE email = ?;",
                (clean_email,)
            )
            row = cursor.fetchone()

            # Generic error message to prevent email enumeration
            if not row or not verify_password(password, row["password_hash"]):
                return False, None, "Invalid email or password."

            user_data = {
                "id": row["id"],
                "full_name": row["full_name"],
                "email": row["email"],
            }
            return True, user_data, "Login successful."
    except Exception as err:
        return False, None, f"Database error during authentication: {str(err)}"


# ==============================================================================
# USER-SCOPED REPOSITORY BOOKMARKS
# ==============================================================================

def get_user_saved_repos(user_id: int) -> List[str]:
    """Retrieve list of saved repository slugs for an authenticated user."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT repo_name FROM user_saved_repos WHERE user_id = ? ORDER BY saved_at DESC;",
                (user_id,)
            )
            rows = cursor.fetchall()
            return [row["repo_name"] for row in rows]
    except Exception:
        return []


def add_user_saved_repo(user_id: int, repo_name: str) -> bool:
    """Bookmark a repository for an authenticated user."""
    clean_repo = repo_name.strip()
    if not clean_repo:
        return False
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO user_saved_repos (user_id, repo_name) VALUES (?, ?);",
                (user_id, clean_repo)
            )
            conn.commit()
            return True
    except Exception:
        return False


def remove_user_saved_repo(user_id: int, repo_name: str) -> bool:
    """Remove a bookmarked repository for an authenticated user."""
    clean_repo = repo_name.strip()
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM user_saved_repos WHERE user_id = ? AND repo_name = ?;",
                (user_id, clean_repo)
            )
            conn.commit()
            return True
    except Exception:
        return False


# Automatically ensure tables are created on module import
init_db()
