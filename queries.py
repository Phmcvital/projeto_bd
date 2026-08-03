"""Consultas da Etapa 1 e consultas avancadas usando a DSL do SQLAlchemy."""

from datetime import datetime

from sqlalchemy import Numeric, case, cast, exists, func, select
from sqlalchemy.orm import aliased, joinedload, selectinload

from models import (
    Atendimento,
    Escala,
    Paciente,
    Pessoa,
    Preceptor,
    Procedimento,
    ProcedimentoRealizado,
    Profissional,
    Residente,
    Unidade,
)


def ranking_residentes_por_atendimentos(sessao) -> list:
    comando = (
        select(
            Pessoa.nome.label("nome_residente"),
            func.count(Atendimento.id_atendimento).label("total_atendimentos"),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .group_by(Residente.id_profissional, Pessoa.nome)
        .order_by(func.count(Atendimento.id_atendimento).desc(), Pessoa.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def preceptores_com_mais_de_n_atendimentos_no_mes(
    sessao, mes_ano: str, minimo: int = 1
) -> list:
    inicio = datetime.strptime(mes_ano, "%Y-%m")
    if inicio.month == 12:
        fim = inicio.replace(year=inicio.year + 1, month=1)
    else:
        fim = inicio.replace(month=inicio.month + 1)

    comando = (
        select(
            Pessoa.nome.label("nome_preceptor"),
            func.count(Atendimento.id_atendimento).label("total_atendimentos"),
        )
        .select_from(Preceptor)
        .join(Profissional, Profissional.id_pessoa == Preceptor.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .join(Atendimento, Atendimento.id_preceptor == Preceptor.id_profissional)
        .where(Atendimento.data_hora >= inicio, Atendimento.data_hora < fim)
        .group_by(Preceptor.id_profissional, Pessoa.nome)
        .having(func.count(Atendimento.id_atendimento) > minimo)
        .order_by(func.count(Atendimento.id_atendimento).desc())
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def plantoes_escalados_por_residente_por_unidade(sessao) -> list:
    comando = (
        select(
            Unidade.nome.label("nome_unidade"),
            Pessoa.nome.label("nome_residente"),
            func.count(Escala.id_escala).label("total_plantoes"),
        )
        .select_from(Escala)
        .join(Unidade, Unidade.id_unidade == Escala.id_unidade)
        .join(Residente, Residente.id_profissional == Escala.id_residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .group_by(Unidade.id_unidade, Unidade.nome, Residente.id_profissional, Pessoa.nome)
        .order_by(Unidade.nome, Pessoa.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def pacientes_sem_procedimento_alto_risco(sessao) -> list:
    procedimento_alto = (
        select(Atendimento.id_atendimento)
        .join(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento,
        )
        .join(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .where(
            Atendimento.id_paciente == Paciente.id_pessoa,
            Procedimento.nivel_risco == "ALTO",
        )
    )
    comando = (
        select(
            Pessoa.nome.label("nome_paciente"),
            Paciente.num_convenio,
        )
        .select_from(Paciente)
        .join(Pessoa, Pessoa.id_pessoa == Paciente.id_pessoa)
        .where(~exists(procedimento_alto))
        .order_by(Pessoa.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


# ============================================================
# Consultas avancadas pedidas na Etapa 2
# ============================================================

def preceptores_de_pacientes_flamenguistas(sessao) -> list:
    pessoa_preceptor = aliased(Pessoa)
    pessoa_paciente = aliased(Pessoa)

    comando = (
        select(
            Preceptor.id_profissional.label("id_preceptor"),
            pessoa_preceptor.nome.label("nome_preceptor"),
        )
        .select_from(Preceptor)
        .join(
            pessoa_preceptor,
            pessoa_preceptor.id_pessoa == Preceptor.id_profissional,
        )
        .join(Atendimento, Atendimento.id_preceptor == Preceptor.id_profissional)
        .join(Residente, Residente.id_profissional == Atendimento.id_residente)
        .join(Paciente, Paciente.id_pessoa == Atendimento.id_paciente)
        .join(pessoa_paciente, pessoa_paciente.id_pessoa == Paciente.id_pessoa)
        .where(pessoa_paciente.is_flamengo.is_(True))
        .distinct()
        .order_by(pessoa_preceptor.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def ultimo_atendimento_por_paciente(sessao) -> list:
    """Carrega o ultimo atendimento e suas relacoes de uma vez (eager loading)."""
    pacientes = sessao.scalars(
        select(Paciente)
        .options(joinedload(Paciente.pessoa))
        .order_by(Paciente.id_pessoa)
    ).all()

    resultado = []
    for paciente in pacientes:
        comando = (
            select(Atendimento)
            .options(
                joinedload(Atendimento.residente)
                .joinedload(Residente.profissional)
                .joinedload(Profissional.pessoa),
                joinedload(Atendimento.preceptor)
                .joinedload(Preceptor.profissional)
                .joinedload(Profissional.pessoa),
                selectinload(Atendimento.procedimentos_realizados)
                .joinedload(ProcedimentoRealizado.procedimento),
            )
            .where(Atendimento.id_paciente == paciente.id_pessoa)
            .order_by(Atendimento.data_hora.desc())
            .limit(1)
        )
        ultimo = sessao.scalar(comando)

        if ultimo is None:
            resultado.append({
                "paciente": paciente.pessoa.nome,
                "data_hora": None,
                "residente": None,
                "preceptor": None,
                "procedimentos": [],
            })
            continue

        resultado.append({
            "paciente": paciente.pessoa.nome,
            "data_hora": ultimo.data_hora,
            "residente": ultimo.residente.profissional.pessoa.nome,
            "preceptor": ultimo.preceptor.profissional.pessoa.nome,
            "procedimentos": [
                item.procedimento.nome
                for item in ultimo.procedimentos_realizados
            ],
        })
    return resultado


def percentual_alto_risco_por_residente(sessao) -> list:
    total_alto = func.sum(
        case(
            (Procedimento.nivel_risco == "ALTO", ProcedimentoRealizado.quantidade),
            else_=0,
        )
    )
    total_geral = func.sum(ProcedimentoRealizado.quantidade)
    percentual = func.coalesce(
        100.0 * total_alto / func.nullif(total_geral, 0),
        0.0,
    )

    comando = (
        select(
            Residente.id_profissional.label("id_residente"),
            Pessoa.nome.label("nome_residente"),
            func.round(cast(percentual, Numeric), 2).label(
                "percentual_alto_risco"
            ),
        )
        .select_from(Residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(Pessoa, Pessoa.id_pessoa == Profissional.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .outerjoin(
            ProcedimentoRealizado,
            ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento,
        )
        .outerjoin(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .group_by(Residente.id_profissional, Pessoa.nome)
        .order_by(Pessoa.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def demonstrar_lazy_e_eager_loading(sessao, id_paciente: int = 1) -> dict:
    # Lazy: a lista de atendimentos so e consultada quando o atributo e acessado.
    paciente_lazy = sessao.get(Paciente, id_paciente)
    total_lazy = len(paciente_lazy.atendimentos)

    # Eager: selectinload traz a lista junto com a consulta planejada.
    comando = (
        select(Paciente)
        .options(selectinload(Paciente.atendimentos))
        .where(Paciente.id_pessoa == id_paciente)
    )
    paciente_eager = sessao.scalar(comando)

    return {
        "paciente": id_paciente,
        "total_lazy": total_lazy,
        "total_eager": len(paciente_eager.atendimentos),
    }
