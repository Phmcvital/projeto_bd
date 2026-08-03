"""Operacoes CRUD da Etapa 1 reimplementadas com SQLAlchemy."""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from models import (
    Atendimento,
    Paciente,
    Pessoa,
    Preceptor,
    ProcedimentoRealizado,
    Profissional,
    Residente,
    Unidade,
)


class RegistroNaoEncontrado(Exception):
    pass


def _data(valor: str) -> date:
    return date.fromisoformat(valor)


def _data_hora(valor: str) -> datetime:
    return datetime.fromisoformat(valor)


def _salvar(sessao) -> None:
    try:
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise


def inserir_atendimento(
    sessao,
    data_hora: str,
    duracao_minutos: int,
    id_paciente: int,
    id_residente: int,
    id_preceptor: int,
    id_unidade: int = 1,
) -> int:
    if sessao.get(Paciente, id_paciente) is None:
        raise RegistroNaoEncontrado(f"Paciente {id_paciente} nao existe.")
    if sessao.get(Residente, id_residente) is None:
        raise RegistroNaoEncontrado(f"Residente {id_residente} nao existe.")
    if sessao.get(Preceptor, id_preceptor) is None:
        raise RegistroNaoEncontrado(f"Preceptor {id_preceptor} nao existe.")
    if sessao.get(Unidade, id_unidade) is None:
        raise RegistroNaoEncontrado(f"Unidade {id_unidade} nao existe.")

    atendimento = Atendimento(
        data_hora=_data_hora(data_hora),
        duracao_minutos=duracao_minutos,
        id_paciente=id_paciente,
        id_residente=id_residente,
        id_preceptor=id_preceptor,
        id_unidade=id_unidade,
    )
    sessao.add(atendimento)
    _salvar(sessao)
    return atendimento.id_atendimento


def listar_atendimentos_por_paciente(sessao, id_paciente: int) -> list:
    comando = (
        select(Atendimento)
        .options(
            joinedload(Atendimento.residente)
            .joinedload(Residente.profissional)
            .joinedload(Profissional.pessoa),
            joinedload(Atendimento.preceptor)
            .joinedload(Preceptor.profissional)
            .joinedload(Profissional.pessoa),
            joinedload(Atendimento.unidade),
        )
        .where(Atendimento.id_paciente == id_paciente)
        .order_by(Atendimento.data_hora)
    )
    atendimentos = sessao.scalars(comando).all()
    return [
        {
            "id_atendimento": item.id_atendimento,
            "data_hora": item.data_hora,
            "duracao_minutos": item.duracao_minutos,
            "nome_residente": item.residente.profissional.pessoa.nome,
            "nome_preceptor": item.preceptor.profissional.pessoa.nome,
            "nome_unidade": item.unidade.nome,
        }
        for item in atendimentos
    ]


def listar_procedimentos_de_atendimento(sessao, id_atendimento: int) -> list:
    comando = (
        select(ProcedimentoRealizado)
        .options(joinedload(ProcedimentoRealizado.procedimento))
        .where(ProcedimentoRealizado.id_atendimento == id_atendimento)
    )
    itens = sessao.scalars(comando).all()
    itens.sort(key=lambda item: item.procedimento.nome)
    return [
        {
            "nome_procedimento": item.procedimento.nome,
            "quantidade": item.quantidade,
            "tempo_real_minutos": item.tempo_real_minutos,
            "observacao": item.observacao,
        }
        for item in itens
    ]


def atualizar_paciente(
    sessao,
    id_paciente: int,
    nome: str | None = None,
    cpf: str | None = None,
    data_nascimento: str | None = None,
    is_flamengo: int | None = None,
    telefone: str | None = None,
    num_convenio: str | None = None,
    alergias: str | None = None,
    grupo_sanguineo: str | None = None,
) -> None:
    paciente = sessao.get(Paciente, id_paciente)
    if paciente is None:
        raise RegistroNaoEncontrado(f"Paciente {id_paciente} nao existe.")

    pessoa = paciente.pessoa
    if nome is not None:
        pessoa.nome = nome
    if cpf is not None:
        pessoa.cpf = cpf
    if data_nascimento is not None:
        pessoa.data_nascimento = _data(data_nascimento)
    if is_flamengo is not None:
        pessoa.is_flamengo = bool(is_flamengo)
    if telefone is not None:
        pessoa.telefone = telefone
    if num_convenio is not None:
        paciente.num_convenio = num_convenio
    if alergias is not None:
        paciente.alergias = alergias
    if grupo_sanguineo is not None:
        paciente.grupo_sanguineo = grupo_sanguineo

    _salvar(sessao)


def atualizar_profissional(
    sessao,
    id_profissional: int,
    nome: str | None = None,
    cpf: str | None = None,
    data_nascimento: str | None = None,
    is_flamengo: int | None = None,
    telefone: str | None = None,
    crm: str | None = None,
    data_admissao: str | None = None,
    especialidade: str | None = None,
    info_tipo: str | None = None,
) -> None:
    profissional = sessao.get(Profissional, id_profissional)
    if profissional is None:
        raise RegistroNaoEncontrado(f"Profissional {id_profissional} nao existe.")

    pessoa = profissional.pessoa
    if nome is not None:
        pessoa.nome = nome
    if cpf is not None:
        pessoa.cpf = cpf
    if data_nascimento is not None:
        pessoa.data_nascimento = _data(data_nascimento)
    if is_flamengo is not None:
        pessoa.is_flamengo = bool(is_flamengo)
    if telefone is not None:
        pessoa.telefone = telefone
    if crm is not None:
        profissional.crm = crm
    if data_admissao is not None:
        profissional.data_admissao = _data(data_admissao)
    if especialidade is not None:
        profissional.especialidade = especialidade

    if info_tipo is not None:
        if profissional.preceptor is not None:
            profissional.preceptor.titulacao = info_tipo
        elif profissional.residente is not None:
            profissional.residente.ano_residencia = info_tipo

    _salvar(sessao)


def remover_procedimento_realizado(
    sessao, id_atendimento: int, id_procedimento: int
) -> bool:
    chave = (id_atendimento, id_procedimento)
    realizado = sessao.get(ProcedimentoRealizado, chave)
    if realizado is None:
        raise RegistroNaoEncontrado("Procedimento realizado nao encontrado.")
    if realizado.faturado:
        return False

    sessao.delete(realizado)
    _salvar(sessao)
    return True


def tempo_medio_por_residente(sessao) -> list:
    comando = (
        select(
            Pessoa.nome.label("nome_residente"),
            func.avg(Atendimento.duracao_minutos).label("media_duracao_minutos"),
            func.count(Atendimento.id_atendimento).label("total_atendimentos"),
        )
        .join(Residente, Residente.id_profissional == Pessoa.id_pessoa)
        .join(Atendimento, Atendimento.id_residente == Residente.id_profissional)
        .group_by(Pessoa.id_pessoa, Pessoa.nome)
        .order_by(Pessoa.nome)
    )
    return [dict(linha._mapping) for linha in sessao.execute(comando)]


def inserir_paciente(
    sessao,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone: str | None,
    num_convenio: str | None,
    alergias: str | None,
    grupo_sanguineo: str | None,
) -> int:
    pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=_data(data_nascimento),
        is_flamengo=bool(is_flamengo),
        telefone=telefone,
    )
    pessoa.paciente = Paciente(
        num_convenio=num_convenio,
        alergias=alergias,
        grupo_sanguineo=grupo_sanguineo,
    )
    sessao.add(pessoa)
    _salvar(sessao)
    return pessoa.id_pessoa


def listar_pacientes(sessao) -> list:
    comando = (
        select(Paciente)
        .options(joinedload(Paciente.pessoa))
        .order_by(Paciente.id_pessoa)
    )
    pacientes = sessao.scalars(comando).all()
    return [
        {
            "id_pessoa": paciente.id_pessoa,
            "nome": paciente.pessoa.nome,
            "cpf": paciente.pessoa.cpf,
            "data_nascimento": paciente.pessoa.data_nascimento,
            "is_flamengo": paciente.pessoa.is_flamengo,
            "telefone": paciente.pessoa.telefone,
            "num_convenio": paciente.num_convenio,
            "alergias": paciente.alergias,
            "grupo_sanguineo": paciente.grupo_sanguineo,
        }
        for paciente in pacientes
    ]


def inserir_profissional(
    sessao,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone: str | None,
    crm: str,
    data_admissao: str,
    especialidade: str,
    tipo: str,
    info_tipo: str,
) -> int:
    pessoa = Pessoa(
        nome=nome,
        cpf=cpf,
        data_nascimento=_data(data_nascimento),
        is_flamengo=bool(is_flamengo),
        telefone=telefone,
    )
    profissional = Profissional(
        crm=crm,
        data_admissao=_data(data_admissao),
        especialidade=especialidade,
    )
    pessoa.profissional = profissional

    if tipo == "preceptor":
        profissional.preceptor = Preceptor(titulacao=info_tipo)
    elif tipo == "residente":
        profissional.residente = Residente(ano_residencia=info_tipo)
    else:
        raise ValueError("Tipo deve ser 'preceptor' ou 'residente'.")

    sessao.add(pessoa)
    _salvar(sessao)
    return pessoa.id_pessoa


def listar_profissionais(sessao) -> list:
    comando = (
        select(Profissional)
        .options(
            joinedload(Profissional.pessoa),
            joinedload(Profissional.preceptor),
            joinedload(Profissional.residente),
        )
        .order_by(Profissional.id_pessoa)
    )
    profissionais = sessao.scalars(comando).all()
    resultado = []
    for profissional in profissionais:
        if profissional.preceptor is not None:
            tipo = "preceptor"
            detalhe = profissional.preceptor.titulacao
        else:
            tipo = "residente"
            detalhe = profissional.residente.ano_residencia

        resultado.append({
            "id_pessoa": profissional.id_pessoa,
            "nome": profissional.pessoa.nome,
            "cpf": profissional.pessoa.cpf,
            "data_nascimento": profissional.pessoa.data_nascimento,
            "is_flamengo": profissional.pessoa.is_flamengo,
            "telefone": profissional.pessoa.telefone,
            "crm": profissional.crm,
            "data_admissao": profissional.data_admissao,
            "especialidade": profissional.especialidade,
            "tipo": tipo,
            "detalhe": detalhe,
        })
    return resultado


def remover_pessoa(sessao, id_pessoa: int) -> bool:
    pessoa = sessao.get(Pessoa, id_pessoa)
    if pessoa is None:
        return False
    sessao.delete(pessoa)
    _salvar(sessao)
    return True


def listar_unidades(sessao) -> list:
    unidades = sessao.scalars(select(Unidade).order_by(Unidade.nome)).all()
    return [
        {"id_unidade": item.id_unidade, "nome": item.nome, "tipo": item.tipo}
        for item in unidades
    ]
