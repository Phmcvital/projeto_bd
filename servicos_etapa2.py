"""Chamadas simples aos objetos PostgreSQL criados na Etapa 2."""

import json

from sqlalchemy import text


def registrar_atendimento_completo(sessao, dados: dict, procedimentos: list[dict]) -> None:
    comando = text("""
        CALL sp_registrar_atendimento_completo(
            CAST(:data_hora AS TIMESTAMP),
            :duracao_minutos,
            :id_paciente,
            :id_residente,
            :id_preceptor,
            :id_unidade,
            CAST(:procedimentos AS JSONB)
        )
    """)
    parametros = dict(dados)
    parametros["procedimentos"] = json.dumps(procedimentos)
    try:
        sessao.execute(comando, parametros)
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise


def calcular_tempo_medio_espera(sessao) -> list:
    try:
        sessao.execute(text("CALL sp_calcular_tempo_medio_espera()"))
        linhas = sessao.execute(
            text("SELECT * FROM resultado_tempo_medio_espera ORDER BY unidade")
        )
        resultado = [dict(linha._mapping) for linha in linhas]
        sessao.commit()
        return resultado
    except Exception:
        sessao.rollback()
        raise


def reajustar_escala(
    sessao,
    id_residente: int,
    dia_origem: str,
    turno_origem: str,
    dia_destino: str,
    turno_destino: str,
) -> None:
    comando = text("""
        CALL sp_reajustar_escala(
            :id_residente, :dia_origem, :turno_origem,
            :dia_destino, :turno_destino
        )
    """)
    try:
        sessao.execute(comando, {
            "id_residente": id_residente,
            "dia_origem": dia_origem,
            "turno_origem": turno_origem,
            "dia_destino": dia_destino,
            "turno_destino": turno_destino,
        })
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise


VIEWS_PERMITIDAS = {
    "internados": "vw_pacientes_internados",
    "sem_supervisor": "vw_residentes_sem_supervisor",
    "estatisticas": "vw_estatisticas_atendimentos_mensal",
}


def consultar_view(sessao, chave: str) -> list:
    nome_view = VIEWS_PERMITIDAS[chave]
    linhas = sessao.execute(text(f"SELECT * FROM {nome_view}"))
    return [dict(linha._mapping) for linha in linhas]


def listar_auditoria(sessao, limite: int = 20) -> list:
    linhas = sessao.execute(
        text("""
            SELECT id_auditoria, id_atendimento, operacao, usuario, data_hora,
                   dados_antigos, dados_novos
            FROM AUDITORIA_ATENDIMENTO
            ORDER BY id_auditoria DESC
            LIMIT :limite
        """),
        {"limite": limite},
    )
    return [dict(linha._mapping) for linha in linhas]
