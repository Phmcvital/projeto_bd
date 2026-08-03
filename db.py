import os
import psycopg2
import psycopg2.extras
from pathlib import Path
from sqlalchemy import create_engine as _sa_create_engine
from sqlalchemy.engine import Engine

BASE_DIR = Path(__file__).parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed_data.sql"
PROCEDURES_PATH = BASE_DIR / "procedures.sql"
TRIGGERS_PATH = BASE_DIR / "triggers.sql"
VIEWS_PATH = BASE_DIR / "views.sql"

env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()


def _db_params() -> dict:
    return {
        "host": os.environ.get("DB_HOST", "localhost"),
        "port": os.environ.get("DB_PORT", "5432"),
        "dbname": os.environ.get("DB_NAME", "hospital"),
        "user": os.environ.get("DB_USER", "postgres"),
        "password": os.environ.get("DB_PASSWORD", "postgres"),
    }


def get_connection() -> psycopg2.extensions.connection:
    params = _db_params()
    return psycopg2.connect(
        **params,
        cursor_factory=psycopg2.extras.DictCursor,
    )


def get_engine() -> Engine:
    p = _db_params()
    url = (
        f"postgresql+psycopg2://{p['user']}:{p['password']}"
        f"@{p['host']}:{p['port']}/{p['dbname']}"
    )
    return _sa_create_engine(url)


def _run_script(conn: psycopg2.extensions.connection, path: Path) -> None:
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)


def init_db(reset: bool = True, seed: bool = True) -> psycopg2.extensions.connection:
    conn = get_connection()
    if reset:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            cur.execute("GRANT ALL ON SCHEMA public TO public;")
        conn.commit()

    _run_script(conn, SCHEMA_PATH)
    conn.commit()

    for path in (PROCEDURES_PATH, TRIGGERS_PATH, VIEWS_PATH):
        _run_script(conn, path)
        conn.commit()

    if seed:
        _run_script(conn, SEED_PATH)
        conn.commit()

    return conn


if __name__ == "__main__":
    conn = init_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM PESSOA;")
        print(f"Banco inicializado. Total de pessoas: {cur.fetchone()['n']}")
    conn.close()
