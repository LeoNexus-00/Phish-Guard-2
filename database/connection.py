"""
database/connection.py - MySQL connection factory for PhishGuard.

Environment variables / Streamlit Secrets:
    DB_HOST      MySQL server host        (default: localhost)
    DB_PORT      MySQL port               (default: 3306)
    DB_USER      MySQL username           (default: root)
    DB_PASSWORD  MySQL password           (required for DB)
    DB_NAME      Database name            (default: phishguard_db)

Local PowerShell setup:
    $env:DB_HOST     = "localhost"
    $env:DB_PORT     = "3306"
    $env:DB_USER     = "root"
    $env:DB_PASSWORD = "your_password_here"
    $env:DB_NAME     = "phishguard_db"

Streamlit Cloud setup:
    Add DB_HOST, DB_USER, DB_PASSWORD, DB_NAME to Streamlit Cloud App Secrets.
"""

import os
import mysql.connector
from mysql.connector import Error


def _get_setting(key, default=None):
    """Retrieve setting from st.secrets (if running in Streamlit) or os.environ."""
    try:
        import streamlit as st
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


def get_connection():
    """
    Open and return a new MySQL connection.

    Returns:
        mysql.connector.connection.MySQLConnection

    Raises:
        RuntimeError: if DB_PASSWORD is not set or connection fails.
                      Password is never included in the error message.
    """
    password = _get_setting("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "[PhishGuard DB] DB_PASSWORD is not configured. "
            "(Local: set $env:DB_PASSWORD; Cloud: set in Streamlit Secrets). "
            "Using JSON backup."
        )

    config = {
        "host":     _get_setting("DB_HOST", "localhost"),
        "port":     int(_get_setting("DB_PORT", 3306)),
        "user":     _get_setting("DB_USER", "root"),
        "password": password,
        "database": _get_setting("DB_NAME", "phishguard_db"),
        "charset":  "utf8mb4",
    }

    try:
        connection = mysql.connector.connect(**config)
        return connection
    except Error as error:
        # Error code, NOT the password, is included in the message.
        raise RuntimeError(
            f"[PhishGuard DB] Could not connect to MySQL "
            f"(host={config['host']}, port={config['port']}, "
            f"user={config['user']}, db={config['database']}). "
            f"MySQL error code: {error.errno}. "
            "Check that MySQL is running and your credentials are correct."
        ) from None
