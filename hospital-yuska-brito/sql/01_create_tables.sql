-- DDL: Criação das tabelas do Sistema de Gestão Hospitalar
-- Banco: PostgreSQL

CREATE TABLE PESSOA (
    id_pessoa       SERIAL       PRIMARY KEY,
    nome            VARCHAR(100) NOT NULL,
    cpf             CHAR(11)     UNIQUE NOT NULL,
    data_nascimento DATE,
    is_flamengo     BOOLEAN      DEFAULT FALSE,
    telefone        VARCHAR(20)
);

CREATE TABLE PACIENTE (
    id_pessoa       INTEGER    PRIMARY KEY REFERENCES PESSOA(id_pessoa),
    num_convenio    VARCHAR(50),
    alergias        TEXT,
    grupo_sanguineo VARCHAR(3) CHECK (grupo_sanguineo IN ('A+','A-','B+','B-','AB+','AB-','O+','O-'))
);

CREATE TABLE PROFISSIONAL (
    id_pessoa     INTEGER      PRIMARY KEY REFERENCES PESSOA(id_pessoa),
    crm           VARCHAR(20)  UNIQUE NOT NULL,
    data_admissao DATE         NOT NULL,
    especialidade VARCHAR(100)
);

CREATE TABLE PRECEPTOR (
    id_profissional INTEGER      PRIMARY KEY REFERENCES PROFISSIONAL(id_pessoa),
    titulacao       VARCHAR(100)
);

CREATE TABLE RESIDENTE (
    id_profissional INTEGER PRIMARY KEY REFERENCES PROFISSIONAL(id_pessoa),
    ano_residencia  CHAR(4) NOT NULL CHECK (ano_residencia ~ '^\d{4}$')
);

CREATE TABLE UNIDADE (
    id_unidade        SERIAL       PRIMARY KEY,
    nome              VARCHAR(100) NOT NULL,
    capacidade_leitos INTEGER      CHECK (capacidade_leitos > 0)
);

CREATE TABLE PROCEDIMENTO (
    id_procedimento        SERIAL       PRIMARY KEY,
    nome                   VARCHAR(150) NOT NULL,
    nivel_risco            VARCHAR(5)   NOT NULL CHECK (nivel_risco IN ('BAIXO','MEDIO','ALTO')),
    tempo_estimado_minutos INTEGER      CHECK (tempo_estimado_minutos > 0)
);

CREATE TABLE ATENDIMENTO (
    id_atendimento  SERIAL       PRIMARY KEY,
    data_hora       TIMESTAMP    NOT NULL,
    duracao_minutos NUMERIC(8,2),
    id_paciente     INTEGER      NOT NULL REFERENCES PACIENTE(id_pessoa),
    id_residente    INTEGER      NOT NULL REFERENCES RESIDENTE(id_profissional),
    id_preceptor    INTEGER      NOT NULL REFERENCES PRECEPTOR(id_profissional),
    id_unidade      INTEGER      REFERENCES UNIDADE(id_unidade)
);

CREATE TABLE PROCEDIMENTO_REALIZADO (
    id_atendimento     INTEGER NOT NULL REFERENCES ATENDIMENTO(id_atendimento),
    id_procedimento    INTEGER NOT NULL REFERENCES PROCEDIMENTO(id_procedimento),
    quantidade         INTEGER NOT NULL DEFAULT 1 CHECK (quantidade > 0),
    tempo_real_minutos INTEGER,
    observacao         TEXT,
    faturado           BOOLEAN NOT NULL DEFAULT FALSE,
    PRIMARY KEY (id_atendimento, id_procedimento)
);

CREATE TABLE ESCALA_PLANTAO (
    id_escala        SERIAL    PRIMARY KEY,
    id_residente     INTEGER   NOT NULL REFERENCES RESIDENTE(id_profissional),
    id_unidade       INTEGER   NOT NULL REFERENCES UNIDADE(id_unidade),
    data_hora_inicio TIMESTAMP NOT NULL,
    data_hora_fim    TIMESTAMP NOT NULL,
    CHECK (data_hora_fim > data_hora_inicio)
);
