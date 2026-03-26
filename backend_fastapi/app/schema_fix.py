# app/schema_fix.py
from sqlalchemy import text
from sqlalchemy.engine import Engine


def _sqlite_table_columns(engine: Engine, table: str) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text(f"PRAGMA table_info({table})")).mappings().all()
    return {r["name"] for r in rows}


def ensure_users_table_has_expected_columns(engine: Engine) -> None:
    """
    Hotfix seguro para DEV (SQLite):
    - Se a tabela users já existe mas faltam colunas que o model espera,
      adiciona via ALTER TABLE.
    """
    with engine.connect() as conn:
        table_exists = conn.execute(
            text("SELECT 1 FROM sqlite_master WHERE type='table' AND name='users'")
        ).first() is not None

    if not table_exists:
        return

    cols = _sqlite_table_columns(engine, "users")

    # Colunas que seu stacktrace mostra que o ORM espera
    expected = {
        "username": "VARCHAR",
        "full_name": "VARCHAR",
        "email": "VARCHAR",
        "hashed_password": "VARCHAR",   # <-- ESSA é a que está faltando agora
        "is_active": "BOOLEAN",
        "is_superuser": "BOOLEAN",
        "created_at": "DATETIME",
        "updated_at": "DATETIME",
    }

    missing = [(name, typ) for name, typ in expected.items() if name not in cols]
    if not missing:
        return

    with engine.begin() as conn:
        for name, typ in missing:
            conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {typ}"))
