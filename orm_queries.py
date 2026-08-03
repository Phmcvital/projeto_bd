from sqlalchemy import select, func, case, distinct, Float, cast
from sqlalchemy.orm import Session, joinedload, aliased
from orm_models import (
    Pessoa, Paciente, Profissional, Preceptor, Residente,
    Unidade, Atendimento, Procedimento, ProcedimentoRealizado, Escala,
)


def preceptores_que_supervisionaram_flamenguistas(session: Session) -> list[str]:
    PessoaPreceptor = aliased(Pessoa, name='pessoa_preceptor')
    PessoaPaciente = aliased(Pessoa, name='pessoa_paciente')
    stmt = (
        select(distinct(PessoaPreceptor.nome))
        .select_from(Preceptor)
        .join(Profissional, Preceptor.id_profissional == Profissional.id_pessoa)
        .join(PessoaPreceptor, Profissional.id_pessoa == PessoaPreceptor.id_pessoa)
        .join(Atendimento, Atendimento.id_preceptor == Preceptor.id_profissional)
        .join(Paciente, Paciente.id_pessoa == Atendimento.id_paciente)
        .join(PessoaPaciente, Paciente.id_pessoa == PessoaPaciente.id_pessoa)
        .where(PessoaPaciente.is_flamengo == 1)
    )
    return session.execute(stmt).scalars().all()


def ultimo_atendimento_por_paciente(session: Session) -> list:
    subq = (
        select(func.max(Atendimento.id_atendimento).label('max_id'))
        .group_by(Atendimento.id_paciente)
        .subquery()
    )
    stmt = (
        select(Atendimento)
        .join(subq, Atendimento.id_atendimento == subq.c.max_id)
        .options(
            joinedload(Atendimento.procedimentos_realizados)
                .joinedload(ProcedimentoRealizado.procedimento),
            joinedload(Atendimento.preceptor)
                .joinedload(Preceptor.profissional)
                .joinedload(Profissional.pessoa),
        )
    )
    return session.execute(stmt).unique().scalars().all()


def percentual_alto_risco_por_residente(session: Session) -> list:
    PessoaRes = aliased(Pessoa, name='pessoa_residente')
    stmt = (
        select(
            PessoaRes.nome,
            (
                cast(func.count(case((Procedimento.nivel_risco == 'ALTO', 1))), Float)
                / cast(func.count(Procedimento.id_procedimento), Float)
                * 100
            ).label('percentual_alto_risco'),
        )
        .select_from(Residente)
        .join(Profissional, Residente.id_profissional == Profissional.id_pessoa)
        .join(PessoaRes, Profissional.id_pessoa == PessoaRes.id_pessoa)
        .join(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .join(ProcedimentoRealizado, ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento)
        .join(Procedimento, Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento)
        .group_by(Residente.id_profissional, PessoaRes.nome)
        .order_by(
            cast(func.count(case((Procedimento.nivel_risco == 'ALTO', 1))), Float).desc()
        )
    )
    return session.execute(stmt).all()


def ranking_residentes_por_atendimentos(session: Session) -> list:
    PessoaRes = aliased(Pessoa, name='pessoa_res_rank')
    stmt = (
        select(
            PessoaRes.nome.label('nome_residente'),
            func.count(Atendimento.id_atendimento).label('total_atendimentos'),
        )
        .select_from(Residente)
        .join(Profissional, Residente.id_profissional == Profissional.id_pessoa)
        .join(PessoaRes, Profissional.id_pessoa == PessoaRes.id_pessoa)
        .outerjoin(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .group_by(Residente.id_profissional, PessoaRes.nome)
        .order_by(func.count(Atendimento.id_atendimento).desc())
    )
    return session.execute(stmt).all()


def plantoes_escalados_por_residente_por_unidade(session: Session) -> list:
    PessoaRes = aliased(Pessoa, name='pessoa_res_esc')
    stmt = (
        select(
            Unidade.nome.label('nome_unidade'),
            PessoaRes.nome.label('nome_residente'),
            func.count(Escala.id_escala).label('total_plantoes'),
        )
        .select_from(Escala)
        .join(Unidade, Unidade.id_unidade == Escala.id_unidade)
        .join(Residente, Residente.id_profissional == Escala.id_residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(PessoaRes, PessoaRes.id_pessoa == Profissional.id_pessoa)
        .group_by(Unidade.id_unidade, Unidade.nome, Escala.id_residente, PessoaRes.nome)
        .order_by(Unidade.nome, func.count(Escala.id_escala).desc())
    )
    return session.execute(stmt).all()


def tempo_medio_por_residente(session: Session) -> list:
    PessoaRes = aliased(Pessoa, name='pessoa_res_tempo')
    stmt = (
        select(
            PessoaRes.nome.label('nome_residente'),
            func.avg(Atendimento.duracao_minutos).label('media_duracao_minutos'),
            func.count(Atendimento.id_atendimento).label('total_atendimentos'),
        )
        .select_from(Atendimento)
        .join(Residente, Residente.id_profissional == Atendimento.id_residente)
        .join(Profissional, Profissional.id_pessoa == Residente.id_profissional)
        .join(PessoaRes, PessoaRes.id_pessoa == Profissional.id_pessoa)
        .group_by(Atendimento.id_residente, PessoaRes.nome)
        .order_by(func.avg(Atendimento.duracao_minutos).desc())
    )
    return session.execute(stmt).all()


def preceptores_com_mais_de_n_atendimentos_no_mes(
    session: Session, ano_mes: str, minimo: int = 1
) -> list:
    from sqlalchemy import func as f, literal_column
    PessoaPrec = aliased(Pessoa, name='pessoa_prec_mes')
    stmt = (
        select(
            PessoaPrec.nome.label('nome_preceptor'),
            func.count(Atendimento.id_atendimento).label('total_atendimentos'),
        )
        .select_from(Atendimento)
        .join(Preceptor, Preceptor.id_profissional == Atendimento.id_preceptor)
        .join(Profissional, Profissional.id_pessoa == Preceptor.id_profissional)
        .join(PessoaPrec, PessoaPrec.id_pessoa == Profissional.id_pessoa)
        .where(func.to_char(Atendimento.data_hora, 'YYYY-MM') == ano_mes)
        .group_by(Atendimento.id_preceptor, PessoaPrec.nome)
        .having(func.count(Atendimento.id_atendimento) > minimo)
        .order_by(func.count(Atendimento.id_atendimento).desc())
    )
    return session.execute(stmt).all()


def pacientes_sem_procedimento_alto_risco(session: Session) -> list:
    PessoaPac = aliased(Pessoa, name='pessoa_pac_sem_risco')
    subq_alto = (
        select(Atendimento.id_paciente)
        .join(ProcedimentoRealizado, ProcedimentoRealizado.id_atendimento == Atendimento.id_atendimento)
        .join(Procedimento, Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento)
        .where(Procedimento.nivel_risco == 'ALTO')
        .subquery()
    )
    stmt = (
        select(
            PessoaPac.nome.label('nome_paciente'),
            Paciente.num_convenio,
        )
        .join(Paciente, Paciente.id_pessoa == PessoaPac.id_pessoa)
        .where(Paciente.id_pessoa.not_in(select(subq_alto.c.id_paciente)))
        .order_by(PessoaPac.nome)
    )
    return session.execute(stmt).all()
