"""Verificacao automatica e simples das funcionalidades da Etapa 2."""

import json

from sqlalchemy import text

import concorrencia
import queries
from db import SessionLocal, engine


def verificar_objetos() -> None:
    with engine.connect() as conexao:
        assert conexao.scalar(text("SELECT COUNT(*) FROM PESSOA")) == 15

        procedures = conexao.scalar(text("""
            SELECT COUNT(*) FROM pg_proc
            WHERE proname IN (
                'sp_registrar_atendimento_completo',
                'sp_calcular_tempo_medio_espera',
                'sp_reajustar_escala'
            )
        """))
        assert procedures == 3

        triggers = conexao.scalar(text("""
            SELECT COUNT(DISTINCT trigger_name) FROM information_schema.triggers
            WHERE trigger_name IN (
                'trg_check_sobreposicao_escala',
                'trg_audita_atendimento',
                'trg_atualiza_media_procedimentos'
            )
        """))
        assert triggers == 3

        views = conexao.scalar(text("""
            SELECT COUNT(*) FROM information_schema.views
            WHERE table_schema = 'public'
              AND table_name IN (
                  'vw_pacientes_internados',
                  'vw_residentes_sem_supervisor',
                  'vw_estatisticas_atendimentos_mensal'
              )
        """))
        assert views == 3

    print("[OK] 3 procedures, 3 triggers, 3 views e dados encontrados.")


def verificar_procedures_e_triggers() -> None:
    procedimentos = [{
        "id_procedimento": 1,
        "quantidade": 1,
        "data_hora_inicio": "2026-08-02 10:08:00",
        "tempo_real_minutos": 21,
        "observacao": "Teste automatico",
        "faturado": False,
    }]

    with engine.connect() as conexao:
        transacao = conexao.begin()
        antes = conexao.scalar(text("SELECT COUNT(*) FROM ATENDIMENTO"))
        conexao.execute(text("""
            CALL sp_registrar_atendimento_completo(
                CAST(:data_hora AS TIMESTAMP), 40, 1, 11, 6, 1,
                CAST(:procedimentos AS JSONB)
            )
        """), {
            "data_hora": "2026-08-02 10:00:00",
            "procedimentos": json.dumps(procedimentos),
        })
        depois = conexao.scalar(text("SELECT COUNT(*) FROM ATENDIMENTO"))
        assert depois == antes + 1

        ultima_auditoria = conexao.scalar(text("""
            SELECT operacao FROM AUDITORIA_ATENDIMENTO
            ORDER BY id_auditoria DESC LIMIT 1
        """))
        assert ultima_auditoria == "INSERT"
        transacao.rollback()

    with engine.connect() as conexao:
        transacao = conexao.begin()
        conexao.execute(text("CALL sp_calcular_tempo_medio_espera()"))
        total = conexao.scalar(text("""
            SELECT COUNT(*) FROM resultado_tempo_medio_espera
        """))
        assert total > 0
        transacao.rollback()

    with engine.connect() as conexao:
        transacao = conexao.begin()
        conexao.execute(text("""
            CALL sp_reajustar_escala(
                11, 'segunda', 'manha', 'quinta', 'tarde'
            )
        """))
        alterada = conexao.scalar(text("""
            SELECT COUNT(*) FROM ESCALA
            WHERE id_residente = 11
              AND dia_semana = 'quinta'
              AND turno = 'tarde'
        """))
        assert alterada == 1
        transacao.rollback()

    print("[OK] Procedures, transacoes e auditoria funcionando.")


def verificar_views_e_orm() -> None:
    with engine.connect() as conexao:
        assert conexao.scalar(text(
            "SELECT COUNT(*) FROM vw_pacientes_internados"
        )) > 0
        assert conexao.scalar(text(
            "SELECT COUNT(*) FROM vw_residentes_sem_supervisor"
        )) > 0
        assert conexao.scalar(text(
            "SELECT COUNT(*) FROM vw_estatisticas_atendimentos_mensal"
        )) > 0

    sessao = SessionLocal()
    try:
        assert queries.preceptores_de_pacientes_flamenguistas(sessao)
        assert queries.ultimo_atendimento_por_paciente(sessao)
        assert queries.percentual_alto_risco_por_residente(sessao)
        carregamento = queries.demonstrar_lazy_e_eager_loading(sessao, 1)
        assert carregamento["total_lazy"] == carregamento["total_eager"]
    finally:
        sessao.close()

    print("[OK] Views, consultas ORM e lazy/eager loading funcionando.")


def verificar_concorrencia() -> None:
    concorrencia.main()
    concorrencia.preparar_demonstracao()
    print("[OK] Concorrencia executada e dado de teste removido.")


def main() -> None:
    verificar_objetos()
    verificar_procedures_e_triggers()
    verificar_views_e_orm()
    verificar_concorrencia()
    print("\nETAPA 2 VALIDADA COM SUCESSO.")


if __name__ == "__main__":
    main()
