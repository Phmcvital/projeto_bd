from datetime import date, datetime
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from orm_models import (
    Pessoa, Paciente, Profissional, Preceptor, Residente,
    Unidade, Atendimento, ProcedimentoRealizado, Procedimento,
)


class RegistroNaoEncontrado(Exception):
    pass


def inserir_paciente(
    session: Session,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone,
    num_convenio,
    alergias,
    grupo_sanguineo,
) -> int:
    pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=date.fromisoformat(data_nascimento),
        is_flamengo=is_flamengo,
        telefone=telefone,
    )
    session.add(pessoa)
    session.flush()
    session.add(
        Paciente(
            id_pessoa=pessoa.id_pessoa,
            num_convenio=num_convenio,
            alergias=alergias,
            grupo_sanguineo=grupo_sanguineo,
        )
    )
    session.commit()
    return pessoa.id_pessoa


def listar_pacientes(session: Session) -> list:
    stmt = (
        select(Pessoa, Paciente)
        .join(Paciente, Paciente.id_pessoa == Pessoa.id_pessoa)
        .order_by(Pessoa.nome)
    )
    return session.execute(stmt).all()


def atualizar_paciente(session: Session, id_paciente: int, **kwargs) -> None:
    paciente = session.get(Paciente, id_paciente)
    if paciente is None:
        raise RegistroNaoEncontrado(f"Paciente {id_paciente} não existe.")
    pessoa_fields = {'nome', 'cpf', 'data_nascimento', 'is_flamengo', 'telefone'}
    paciente_fields = {'num_convenio', 'alergias', 'grupo_sanguineo'}
    for key, value in kwargs.items():
        if value is not None:
            if key in pessoa_fields:
                setattr(paciente.pessoa, key, value)
            elif key in paciente_fields:
                setattr(paciente, key, value)
    session.commit()


def remover_pessoa(session: Session, id_pessoa: int) -> bool:
    if session.get(Pessoa, id_pessoa) is None:
        return False
    session.execute(delete(Pessoa).where(Pessoa.id_pessoa == id_pessoa))
    session.commit()
    return True


def inserir_profissional(
    session: Session,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone,
    crm: str,
    data_admissao: str,
    especialidade: str,
    tipo: str,
    info_tipo: str,
) -> int:
    pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=date.fromisoformat(data_nascimento),
        is_flamengo=is_flamengo,
        telefone=telefone,
    )
    session.add(pessoa)
    session.flush()
    session.add(
        Profissional(
            id_pessoa=pessoa.id_pessoa,
            crm=crm,
            data_admissao=date.fromisoformat(data_admissao),
            especialidade=especialidade,
        )
    )
    session.flush()
    if tipo.lower() == 'preceptor':
        session.add(Preceptor(id_profissional=pessoa.id_pessoa, titulacao=info_tipo))
    elif tipo.lower() == 'residente':
        session.add(Residente(id_profissional=pessoa.id_pessoa, ano_residencia=info_tipo))
    else:
        raise ValueError("Tipo inválido. Deve ser 'preceptor' ou 'residente'.")
    session.commit()
    return pessoa.id_pessoa


def listar_profissionais(session: Session) -> list:
    stmt = (
        select(Pessoa, Profissional, Preceptor, Residente)
        .join(Profissional, Profissional.id_pessoa == Pessoa.id_pessoa)
        .outerjoin(Preceptor, Preceptor.id_profissional == Profissional.id_pessoa)
        .outerjoin(Residente, Residente.id_profissional == Profissional.id_pessoa)
        .order_by(Pessoa.nome)
    )
    return session.execute(stmt).all()


def atualizar_profissional(session: Session, id_profissional: int, **kwargs) -> None:
    prof = session.get(Profissional, id_profissional)
    if prof is None:
        raise RegistroNaoEncontrado(f"Profissional {id_profissional} não existe.")
    pessoa_fields = {'nome', 'cpf', 'data_nascimento', 'is_flamengo', 'telefone'}
    prof_fields = {'crm', 'data_admissao', 'especialidade'}
    for key, value in kwargs.items():
        if value is not None:
            if key in pessoa_fields:
                setattr(prof.pessoa, key, value)
            elif key in prof_fields:
                setattr(prof, key, value)
            elif key == 'info_tipo':
                if prof.preceptor:
                    prof.preceptor.titulacao = value
                elif prof.residente:
                    prof.residente.ano_residencia = value
    session.commit()


def inserir_atendimento(
    session: Session,
    data_hora,
    duracao_minutos: int,
    id_paciente: int,
    id_residente: int,
    id_preceptor: int,
    id_unidade: int = None,
) -> int:
    if session.get(Paciente, id_paciente) is None:
        raise RegistroNaoEncontrado(f"Paciente {id_paciente} não existe.")
    if session.get(Residente, id_residente) is None:
        raise RegistroNaoEncontrado(f"Residente {id_residente} não existe.")
    if session.get(Preceptor, id_preceptor) is None:
        raise RegistroNaoEncontrado(f"Preceptor {id_preceptor} não existe.")
    dt = datetime.fromisoformat(data_hora) if isinstance(data_hora, str) else data_hora
    atendimento = Atendimento(
        data_hora=dt,
        duracao_minutos=duracao_minutos,
        id_paciente=id_paciente,
        id_residente=id_residente,
        id_preceptor=id_preceptor,
        id_unidade=id_unidade,
    )
    session.add(atendimento)
    session.commit()
    return atendimento.id_atendimento


def listar_atendimentos_por_paciente(session: Session, id_paciente: int) -> list:
    stmt = (
        select(Atendimento)
        .where(Atendimento.id_paciente == id_paciente)
        .order_by(Atendimento.data_hora)
    )
    return session.execute(stmt).scalars().all()


def listar_procedimentos_de_atendimento(session: Session, id_atendimento: int) -> list:
    stmt = (
        select(ProcedimentoRealizado, Procedimento)
        .join(
            Procedimento,
            Procedimento.id_procedimento == ProcedimentoRealizado.id_procedimento,
        )
        .where(ProcedimentoRealizado.id_atendimento == id_atendimento)
        .order_by(Procedimento.nome)
    )
    return session.execute(stmt).all()


def remover_procedimento_realizado(
    session: Session, id_atendimento: int, id_procedimento: int
) -> bool:
    pr = session.get(ProcedimentoRealizado, (id_atendimento, id_procedimento))
    if pr is None:
        raise RegistroNaoEncontrado("Procedimento realizado não encontrado.")
    if pr.faturado == 1:
        return False
    session.delete(pr)
    session.commit()
    return True


def listar_unidades(session: Session) -> list:
    stmt = select(Unidade).order_by(Unidade.nome)
    return session.execute(stmt).scalars().all()
