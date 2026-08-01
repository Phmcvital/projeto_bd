import os
import psycopg2
import psycopg2.extras
from pathlib import Path

BASE_DIR = Path(__file__).parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed_data.sql"
env_path = BASE_DIR / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()


def get_connection() -> psycopg2.extensions.connection:
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    dbname = os.environ.get("DB_NAME", "hospital")
    user = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "postgres")

    conn = psycopg2.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
        cursor_factory=psycopg2.extras.DictCursor 
    )
    return conn


def _run_script(conn: psycopg2.extensions.connection, path: Path) -> None:
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
    if seed:
        _run_script(conn, SEED_PATH)
    conn.commit()
    return conn


if __name__ == "__main__":
    conn = init_db()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS n FROM PESSOA;")
        print(f"Banco inicializado. Total de pessoas cadastradas: {cur.fetchone()['n']}")
    conn.close()
