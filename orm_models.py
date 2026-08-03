from sqlalchemy import (
    Column, Integer, Text, Date, Numeric, ForeignKey,
    UniqueConstraint, TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Pessoa(Base):
    __tablename__ = 'pessoa'
    id_pessoa = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=False)
    cpf = Column(Text, nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    is_flamengo = Column(Integer, nullable=False, default=0)
    telefone = Column(Text)

    paciente = relationship('Paciente', back_populates='pessoa', uselist=False)
    profissional = relationship('Profissional', back_populates='pessoa', uselist=False)


class Paciente(Base):
    __tablename__ = 'paciente'
    id_pessoa = Column(
        Integer,
        ForeignKey('pessoa.id_pessoa', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    num_convenio = Column(Text)
    alergias = Column(Text)
    grupo_sanguineo = Column(Text)

    pessoa = relationship('Pessoa', back_populates='paciente')
    atendimentos = relationship(
        'Atendimento', back_populates='paciente', foreign_keys='Atendimento.id_paciente'
    )
    internacoes = relationship('Internacao', back_populates='paciente')


class Profissional(Base):
    __tablename__ = 'profissional'
    id_pessoa = Column(
        Integer,
        ForeignKey('pessoa.id_pessoa', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    crm = Column(Text, nullable=False, unique=True)
    data_admissao = Column(Date, nullable=False)
    especialidade = Column(Text, nullable=False)

    pessoa = relationship('Pessoa', back_populates='profissional')
    preceptor = relationship('Preceptor', back_populates='profissional', uselist=False)
    residente = relationship('Residente', back_populates='profissional', uselist=False)


class Preceptor(Base):
    __tablename__ = 'preceptor'
    id_profissional = Column(
        Integer,
        ForeignKey('profissional.id_pessoa', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    titulacao = Column(Text, nullable=False)

    profissional = relationship('Profissional', back_populates='preceptor')
    escalas = relationship(
        'Escala', back_populates='preceptor', foreign_keys='Escala.id_preceptor'
    )
    atendimentos_supervisionados = relationship(
        'Atendimento', back_populates='preceptor', foreign_keys='Atendimento.id_preceptor'
    )


class Residente(Base):
    __tablename__ = 'residente'
    id_profissional = Column(
        Integer,
        ForeignKey('profissional.id_pessoa', ondelete='CASCADE', onupdate='CASCADE'),
        primary_key=True,
    )
    ano_residencia = Column(Text, nullable=False)

    profissional = relationship('Profissional', back_populates='residente')
    escalas = relationship(
        'Escala', back_populates='residente', foreign_keys='Escala.id_residente'
    )
    atendimentos = relationship(
        'Atendimento', back_populates='residente', foreign_keys='Atendimento.id_residente'
    )


class Unidade(Base):
    __tablename__ = 'unidade'
    id_unidade = Column(Integer, primary_key=True)
    nome = Column(Text, nullable=False)
    tipo = Column(Text, nullable=False)
    capacidade_leitos = Column(Integer, nullable=False)

    escalas = relationship('Escala', back_populates='unidade')
    atendimentos = relationship('Atendimento', back_populates='unidade')
    internacoes = relationship('Internacao', back_populates='unidade')


class Atendimento(Base):
    __tablename__ = 'atendimento'
    id_atendimento = Column(Integer, primary_key=True)
    data_hora = Column(TIMESTAMP, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    id_paciente = Column(Integer, ForeignKey('paciente.id_pessoa'), nullable=False)
    id_residente = Column(Integer, ForeignKey('residente.id_profissional'), nullable=False)
    id_preceptor = Column(Integer, ForeignKey('preceptor.id_profissional'), nullable=False)
    id_unidade = Column(Integer, ForeignKey('unidade.id_unidade'), nullable=True)

    paciente = relationship(
        'Paciente', back_populates='atendimentos', foreign_keys=[id_paciente]
    )
    residente = relationship(
        'Residente', back_populates='atendimentos', foreign_keys=[id_residente], lazy='joined'
    )
    preceptor = relationship(
        'Preceptor',
        back_populates='atendimentos_supervisionados',
        foreign_keys=[id_preceptor],
    )
    unidade = relationship('Unidade', back_populates='atendimentos')
    procedimentos_realizados = relationship(
        'ProcedimentoRealizado', back_populates='atendimento', lazy='select'
    )


class Procedimento(Base):
    __tablename__ = 'procedimento'
    id_procedimento = Column(Integer, primary_key=True)
    codigo = Column(Text, nullable=False, unique=True)
    nome = Column(Text, nullable=False)
    tempo_medio_minutos = Column(Integer, nullable=False)
    nivel_risco = Column(Text, nullable=False, default='BAIXO')
    media_tempo_procedimento = Column(Numeric(8, 2), nullable=True)

    procedimentos_realizados = relationship(
        'ProcedimentoRealizado', back_populates='procedimento'
    )


class ProcedimentoRealizado(Base):
    __tablename__ = 'procedimento_realizado'
    id_atendimento = Column(
        Integer,
        ForeignKey('atendimento.id_atendimento', ondelete='CASCADE'),
        primary_key=True,
    )
    id_procedimento = Column(
        Integer, ForeignKey('procedimento.id_procedimento'), primary_key=True
    )
    quantidade = Column(Integer, nullable=False)
    tempo_real_minutos = Column(Integer, nullable=False)
    observacao = Column(Text)
    faturado = Column(Integer, nullable=False, default=0)

    atendimento = relationship('Atendimento', back_populates='procedimentos_realizados')
    procedimento = relationship('Procedimento', back_populates='procedimentos_realizados')


class Escala(Base):
    __tablename__ = 'escala'
    __table_args__ = (
        UniqueConstraint('id_unidade', 'dia_semana', 'turno', 'id_residente', name='uq_escala'),
    )
    id_escala = Column(Integer, primary_key=True)
    id_unidade = Column(Integer, ForeignKey('unidade.id_unidade'), nullable=False)
    dia_semana = Column(Text, nullable=False)
    turno = Column(Text, nullable=False)
    id_residente = Column(Integer, ForeignKey('residente.id_profissional'), nullable=False)
    id_preceptor = Column(Integer, ForeignKey('preceptor.id_profissional'), nullable=False)

    unidade = relationship('Unidade', back_populates='escalas')
    residente = relationship(
        'Residente', back_populates='escalas', foreign_keys=[id_residente]
    )
    preceptor = relationship(
        'Preceptor', back_populates='escalas', foreign_keys=[id_preceptor]
    )


class Internacao(Base):
    __tablename__ = 'internacao'
    id_internacao = Column(Integer, primary_key=True)
    id_paciente = Column(
        Integer, ForeignKey('paciente.id_pessoa', ondelete='CASCADE'), nullable=False
    )
    id_unidade = Column(Integer, ForeignKey('unidade.id_unidade'), nullable=False)
    data_entrada = Column(TIMESTAMP, nullable=False)
    data_saida = Column(TIMESTAMP, nullable=True)

    paciente = relationship('Paciente', back_populates='internacoes')
    unidade = relationship('Unidade', back_populates='internacoes')


class AuditoriaAtendimento(Base):
    __tablename__ = 'auditoria_atendimento'
    id_auditoria = Column(Integer, primary_key=True)
    id_atendimento = Column(Integer, nullable=True)
    operacao = Column(Text, nullable=False)
    usuario = Column(Text, nullable=False)
    data_hora = Column(TIMESTAMP, nullable=False, server_default='NOW()')
    dados_antigos = Column(JSONB, nullable=True)
    dados_novos = Column(JSONB, nullable=True)
