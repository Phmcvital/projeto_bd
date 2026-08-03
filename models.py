"""Mapeamento objeto-relacional das tabelas do hospital."""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB


Base = declarative_base()


class Pessoa(Base):
    __tablename__ = "pessoa"

    id_pessoa = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(20), nullable=False, unique=True)
    data_nascimento = Column(Date, nullable=False)
    is_flamengo = Column(Boolean, nullable=False, default=False)
    telefone = Column(String(20))

    paciente = relationship(
        "Paciente", back_populates="pessoa", uselist=False,
        cascade="all, delete-orphan"
    )
    profissional = relationship(
        "Profissional", back_populates="pessoa", uselist=False,
        cascade="all, delete-orphan"
    )


class Paciente(Base):
    __tablename__ = "paciente"

    id_pessoa = Column(
        Integer,
        ForeignKey("pessoa.id_pessoa", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    num_convenio = Column(String(50))
    alergias = Column(Text)
    grupo_sanguineo = Column(String(3))

    pessoa = relationship("Pessoa", back_populates="paciente")
    atendimentos = relationship("Atendimento", back_populates="paciente")
    internacoes = relationship("Internacao", back_populates="paciente")

    __table_args__ = (
        CheckConstraint(
            "grupo_sanguineo IN ('A+','A-','B+','B-','AB+','AB-','O+','O-')",
            name="ck_paciente_grupo_sanguineo",
        ),
    )


class Profissional(Base):
    __tablename__ = "profissional"

    id_pessoa = Column(
        Integer,
        ForeignKey("pessoa.id_pessoa", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    crm = Column(String(20), nullable=False, unique=True)
    data_admissao = Column(Date, nullable=False)
    especialidade = Column(String(100), nullable=False)

    pessoa = relationship("Pessoa", back_populates="profissional")
    preceptor = relationship(
        "Preceptor", back_populates="profissional", uselist=False,
        cascade="all, delete-orphan"
    )
    residente = relationship(
        "Residente", back_populates="profissional", uselist=False,
        cascade="all, delete-orphan"
    )


class Preceptor(Base):
    __tablename__ = "preceptor"

    id_profissional = Column(
        Integer,
        ForeignKey("profissional.id_pessoa", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    titulacao = Column(String(20), nullable=False)

    profissional = relationship("Profissional", back_populates="preceptor")
    atendimentos = relationship("Atendimento", back_populates="preceptor")
    escalas = relationship("Escala", back_populates="preceptor")

    __table_args__ = (
        CheckConstraint(
            "titulacao IN ('especialista','mestre','doutor','livre-docente')",
            name="ck_preceptor_titulacao",
        ),
    )


class Residente(Base):
    __tablename__ = "residente"

    id_profissional = Column(
        Integer,
        ForeignKey("profissional.id_pessoa", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    ano_residencia = Column(String(2), nullable=False)

    profissional = relationship("Profissional", back_populates="residente")
    atendimentos = relationship("Atendimento", back_populates="residente")
    escalas = relationship("Escala", back_populates="residente")

    __table_args__ = (
        CheckConstraint(
            "ano_residencia IN ('R1','R2','R3')",
            name="ck_residente_ano",
        ),
    )


class Unidade(Base):
    __tablename__ = "unidade"

    id_unidade = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    tipo = Column(String(20), nullable=False)
    capacidade_leitos = Column(Integer, nullable=False)

    atendimentos = relationship("Atendimento", back_populates="unidade")
    internacoes = relationship("Internacao", back_populates="unidade")
    escalas = relationship("Escala", back_populates="unidade")

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('Enfermaria','UTI','Pronto-Socorro','Ambulatorio')",
            name="ck_unidade_tipo",
        ),
        CheckConstraint("capacidade_leitos >= 0", name="ck_unidade_capacidade"),
    )


class Atendimento(Base):
    __tablename__ = "atendimento"

    id_atendimento = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, nullable=False)
    duracao_minutos = Column(Integer, nullable=False)
    id_paciente = Column(Integer, ForeignKey("paciente.id_pessoa"), nullable=False)
    id_residente = Column(
        Integer, ForeignKey("residente.id_profissional"), nullable=False
    )
    id_preceptor = Column(
        Integer, ForeignKey("preceptor.id_profissional"), nullable=False
    )
    id_unidade = Column(Integer, ForeignKey("unidade.id_unidade"), nullable=False)

    paciente = relationship("Paciente", back_populates="atendimentos")
    residente = relationship("Residente", back_populates="atendimentos")
    preceptor = relationship("Preceptor", back_populates="atendimentos")
    unidade = relationship("Unidade", back_populates="atendimentos")
    procedimentos_realizados = relationship(
        "ProcedimentoRealizado",
        back_populates="atendimento",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("duracao_minutos > 0", name="ck_atendimento_duracao"),
    )


class Internacao(Base):
    __tablename__ = "internacao"

    id_internacao = Column(Integer, primary_key=True)
    id_paciente = Column(Integer, ForeignKey("paciente.id_pessoa"), nullable=False)
    id_unidade = Column(Integer, ForeignKey("unidade.id_unidade"), nullable=False)
    data_hora_entrada = Column(DateTime, nullable=False)
    data_hora_saida = Column(DateTime)

    paciente = relationship("Paciente", back_populates="internacoes")
    unidade = relationship("Unidade", back_populates="internacoes")

    __table_args__ = (
        CheckConstraint(
            "data_hora_saida IS NULL OR data_hora_saida >= data_hora_entrada",
            name="ck_internacao_datas",
        ),
    )


class Procedimento(Base):
    __tablename__ = "procedimento"

    id_procedimento = Column(Integer, primary_key=True)
    codigo = Column(String(20), nullable=False, unique=True)
    nome = Column(String(150), nullable=False)
    tempo_medio_minutos = Column(Integer, nullable=False)
    nivel_risco = Column(String(5), nullable=False, default="BAIXO")
    media_tempo_procedimento = Column(Numeric(10, 2))

    realizacoes = relationship("ProcedimentoRealizado", back_populates="procedimento")

    __table_args__ = (
        CheckConstraint("tempo_medio_minutos > 0", name="ck_procedimento_tempo"),
        CheckConstraint(
            "nivel_risco IN ('BAIXO','MEDIO','ALTO')",
            name="ck_procedimento_risco",
        ),
    )


class ProcedimentoRealizado(Base):
    __tablename__ = "procedimento_realizado"

    id_atendimento = Column(
        Integer,
        ForeignKey("atendimento.id_atendimento", ondelete="CASCADE"),
        primary_key=True,
    )
    id_procedimento = Column(
        Integer, ForeignKey("procedimento.id_procedimento"), primary_key=True
    )
    quantidade = Column(Integer, nullable=False)
    data_hora_inicio = Column(DateTime, nullable=False)
    tempo_real_minutos = Column(Integer, nullable=False)
    observacao = Column(Text)
    faturado = Column(Boolean, nullable=False, default=False)

    atendimento = relationship("Atendimento", back_populates="procedimentos_realizados")
    procedimento = relationship("Procedimento", back_populates="realizacoes")

    __table_args__ = (
        CheckConstraint("quantidade > 0", name="ck_realizado_quantidade"),
        CheckConstraint("tempo_real_minutos > 0", name="ck_realizado_tempo"),
    )


class Escala(Base):
    __tablename__ = "escala"

    id_escala = Column(Integer, primary_key=True)
    id_unidade = Column(Integer, ForeignKey("unidade.id_unidade"), nullable=False)
    dia_semana = Column(String(10), nullable=False)
    turno = Column(String(5), nullable=False)
    id_residente = Column(
        Integer, ForeignKey("residente.id_profissional"), nullable=False
    )
    id_preceptor = Column(
        Integer, ForeignKey("preceptor.id_profissional"), nullable=False
    )

    unidade = relationship("Unidade", back_populates="escalas")
    residente = relationship("Residente", back_populates="escalas")
    preceptor = relationship("Preceptor", back_populates="escalas")

    __table_args__ = (
        CheckConstraint(
            "dia_semana IN ('segunda','terca','quarta','quinta','sexta','sabado','domingo')",
            name="ck_escala_dia",
        ),
        CheckConstraint(
            "turno IN ('manha','tarde','noite')", name="ck_escala_turno"
        ),
        UniqueConstraint(
            "id_unidade", "dia_semana", "turno", "id_residente",
            name="uq_escala_unidade_horario_residente",
        ),
    )


class AuditoriaAtendimento(Base):
    __tablename__ = "auditoria_atendimento"

    id_auditoria = Column(Integer, primary_key=True)
    id_atendimento = Column(Integer)
    operacao = Column(String(10), nullable=False)
    usuario = Column(String(100), nullable=False)
    data_hora = Column(DateTime, nullable=False)
    dados_antigos = Column(JSONB)
    dados_novos = Column(JSONB)
