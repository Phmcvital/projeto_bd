"""Conexao e inicializacao do banco com SQLAlchemy."""

import os
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker


BASE_DIR = Path(__file__).parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
ETAPA2_PATH = BASE_DIR / "etapa2.sql"
SEED_PATH = BASE_DIR / "seed_data.sql"


def _carregar_env() -> None:
    """Le um .env simples sem adicionar outra biblioteca ao projeto."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return

    with open(env_path, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha and not linha.startswith("#") and "=" in linha:
                chave, valor = linha.split("=", 1)
                os.environ.setdefault(chave.strip(), valor.strip())


_carregar_env()


def _database_url() -> str:
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    banco = os.environ.get("DB_NAME", "hospital")
    usuario = os.environ.get("DB_USER", "postgres")
    senha = quote_plus(os.environ.get("DB_PASSWORD", "postgres"))
    return f"postgresql+psycopg://{usuario}:{senha}@{host}:{port}/{banco}"


engine = create_engine(_database_url(), echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session():
    return SessionLocal()


def _run_script(path: Path) -> None:
    """Executa um arquivo DDL pelo cursor do driver.

    O ORM e usado na aplicacao. O cursor fica restrito a instalacao dos scripts,
    pois arquivos PL/pgSQL possuem varios comandos e blocos com ponto e virgula.
    """
    conexao = engine.raw_connection()
    try:
        with open(path, "r", encoding="utf-8") as arquivo:
            sql = arquivo.read()
        cursor = conexao.cursor()
        cursor.execute(sql)
        cursor.close()
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()


def init_db(reset: bool = True, seed: bool = True):
    if reset:
        with engine.begin() as conexao:
            conexao.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            conexao.execute(text("CREATE SCHEMA public"))
            conexao.execute(text("GRANT ALL ON SCHEMA public TO public"))

    _run_script(SCHEMA_PATH)
    _run_script(ETAPA2_PATH)
    if seed:
        _run_script(SEED_PATH)

    return get_session()


if __name__ == "__main__":
    from models import Pessoa

    sessao = init_db()
    try:
        total = sessao.query(Pessoa).count()
        print(f"Banco inicializado. Total de pessoas cadastradas: {total}")
    finally:
        sessao.close()
