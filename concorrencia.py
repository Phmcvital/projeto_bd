"""
Demonstração de concorrência: duas transações tentam modificar a mesma
linha de ESCALA simultaneamente usando SELECT FOR UPDATE (lock pessimista).
T1 segura o lock por 3 segundos; T2 fica bloqueada até T1 commitar.
"""
import threading
import time
from datetime import datetime
from sqlalchemy import text
from db import get_engine


def log(prefixo: str, msg: str) -> None:
    ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
    print(f"[{ts}] {prefixo}: {msg}", flush=True)


def transacao_1(engine, id_escala: int) -> None:
    with engine.connect() as conn:
        conn.execute(text("BEGIN"))
        log("T1", "transação iniciada")
        row = conn.execute(
            text("SELECT id_escala, dia_semana, turno FROM ESCALA WHERE id_escala = :id FOR UPDATE"),
            {"id": id_escala},
        ).fetchone()
        log("T1", f"lock obtido — escala={row.id_escala} dia={row.dia_semana} turno={row.turno}")

        time.sleep(3)

        try:
            conn.execute(
                text("UPDATE ESCALA SET dia_semana = 'sexta' WHERE id_escala = :id"),
                {"id": id_escala},
            )
            conn.execute(text("COMMIT"))
            log("T1", "commit realizado (dia_semana -> sexta)")
        except Exception as exc:
            conn.execute(text("ROLLBACK"))
            log("T1", f"rollback — {exc}")


def transacao_2(engine, id_escala: int) -> None:
    time.sleep(0.3)
    with engine.connect() as conn:
        conn.execute(text("BEGIN"))
        log("T2", "transação iniciada")
        log("T2", f"tentando lock na escala {id_escala} (vai bloquear)...")
        try:
            row = conn.execute(
                text("SELECT id_escala, dia_semana, turno FROM ESCALA WHERE id_escala = :id FOR UPDATE"),
                {"id": id_escala},
            ).fetchone()
            log("T2", f"lock obtido após T1 commitar — dia_semana={row.dia_semana}")
            conn.execute(
                text("UPDATE ESCALA SET turno = 'noite' WHERE id_escala = :id"),
                {"id": id_escala},
            )
            conn.execute(text("COMMIT"))
            log("T2", "commit realizado (turno -> noite)")
        except Exception as exc:
            conn.execute(text("ROLLBACK"))
            log("T2", f"rollback — {exc}")


def main() -> None:
    engine = get_engine()

    with engine.connect() as conn:
        row = conn.execute(text("SELECT id_escala FROM ESCALA LIMIT 1")).fetchone()
        if row is None:
            print("Banco sem escalas. Execute: python db.py")
            return
        id_escala = row[0]

    print(f"\nDemonstração de lock pessimista — ESCALA id={id_escala}")
    print("=" * 60)

    t1 = threading.Thread(target=transacao_1, args=(engine, id_escala))
    t2 = threading.Thread(target=transacao_2, args=(engine, id_escala))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("=" * 60)
    print("Demonstração concluída.")

    with engine.connect() as conn:
        conn.execute(text("BEGIN"))
        conn.execute(
            text("UPDATE ESCALA SET dia_semana='segunda', turno='manha' WHERE id_escala = :id"),
            {"id": id_escala},
        )
        conn.execute(text("COMMIT"))
        log("MAIN", f"escala {id_escala} restaurada para estado original")


if __name__ == "__main__":
    main()
