"""PostgreSQL connection and database initialization for ORIGIN."""

import os
from pathlib import Path
from typing import Generator

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def connect_to_database() -> psycopg.Connection:
    """Open a new PostgreSQL connection using environment configuration."""
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg.connect(database_url, row_factory=dict_row)

    password = os.getenv("POSTGRES_PASSWORD")
    if not password:
        raise RuntimeError(
            "PostgreSQL credentials are missing. Create a .env file and set "
            "POSTGRES_PASSWORD, or set DATABASE_URL. See .env.example."
        )

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "origin_db"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=password,
        row_factory=dict_row,
    )


def get_db() -> Generator[psycopg.Connection, None, None]:
    """FastAPI dependency: provide one connection per request."""
    connection = connect_to_database()
    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    """Create the schema and insert starter content without overwriting data."""
    from seed_data import seed_default_data

    schema_path = BASE_DIR / "schema.sql"
    schema_sql = schema_path.read_text(encoding="utf-8")

    with connect_to_database() as connection:
        with connection.cursor() as cursor:
            # The schema file contains only standalone DDL statements.
            for statement in schema_sql.split(";"):
                if statement.strip():
                    cursor.execute(statement)
        seed_default_data(connection)
