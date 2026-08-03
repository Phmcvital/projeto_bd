"""Demonstra duas transacoes concorrentes tentando criar a mesma escala."""

import logging
import threading
import time

from sqlalchemy import delete, func, select

from db import SessionLocal
from models import Escala, Residente


ID_RESIDENTE = 11
ID_PRECEPTOR = 6
ID_UNIDADE = 2
DIA = "domingo"
TURNO = "tarde"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(threadName)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("concorrencia.log", mode="w", encoding="utf-8"),
    ],
)


def preparar_demonstracao() -> None:
    """Remove apenas a escala fixa usada pela demonstracao anterior."""
    sessao = SessionLocal()
    try:
        sessao.execute(
            delete(Escala).where(
                Escala.id_residente == ID_RESIDENTE,
                Escala.id_unidade == ID_UNIDADE,
                Escala.dia_semana == DIA,
                Escala.turno == TURNO,
            )
        )
        sessao.commit()
    finally:
        sessao.close()


def tentar_escalar(nome: str, espera_com_lock: int) -> None:
    sessao = SessionLocal()
    try:
        logging.info("%s iniciou a transacao.", nome)

        # FOR UPDATE faz a segunda transacao aguardar a primeira liberar
        # o mesmo residente. Cada thread possui sua propria sessao.
        residente = sessao.scalar(
            select(Residente)
            .where(Residente.id_profissional == ID_RESIDENTE)
            .with_for_update()
        )
        logging.info("%s obteve o bloqueio do residente %s.", nome, residente.id_profissional)

        conflito = sessao.scalar(
            select(Escala).where(
                Escala.id_residente == ID_RESIDENTE,
                Escala.id_unidade == ID_UNIDADE,
                Escala.dia_semana == DIA,
                Escala.turno == TURNO,
            )
        )
        if conflito is not None:
            logging.warning("%s encontrou a escala criada pela outra transacao.", nome)
            sessao.rollback()
            return

        sessao.add(Escala(
            id_residente=ID_RESIDENTE,
            id_preceptor=ID_PRECEPTOR,
            id_unidade=ID_UNIDADE,
            dia_semana=DIA,
            turno=TURNO,
        ))
        logging.info("%s preparou o INSERT e manterá o lock por %s s.", nome, espera_com_lock)
        time.sleep(espera_com_lock)
        sessao.commit()
        logging.info("%s confirmou a transacao (COMMIT).", nome)
    except Exception as erro:
        sessao.rollback()
        logging.exception("%s desfez a transacao: %s", nome, erro)
    finally:
        sessao.close()


def main() -> None:
    preparar_demonstracao()

    primeira = threading.Thread(
        target=tentar_escalar, args=("Transacao 1", 2), name="T1"
    )
    segunda = threading.Thread(
        target=tentar_escalar, args=("Transacao 2", 0), name="T2"
    )

    primeira.start()
    time.sleep(0.3)
    segunda.start()
    primeira.join()
    segunda.join()

    sessao = SessionLocal()
    try:
        total = sessao.scalar(
            select(func.count(Escala.id_escala)).where(
                Escala.id_residente == ID_RESIDENTE,
                Escala.id_unidade == ID_UNIDADE,
                Escala.dia_semana == DIA,
                Escala.turno == TURNO,
            )
        )
        logging.info("Resultado final: %s escala consistente no horario.", total)
    finally:
        sessao.close()


if __name__ == "__main__":
    main()
