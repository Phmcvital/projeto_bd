CREATE TABLE PESSOA (
    id_pessoa SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL UNIQUE,
    data_nascimento DATE NOT NULL,
    is_flamengo INTEGER NOT NULL DEFAULT 0 CHECK (is_flamengo IN (0, 1)),
    telefone TEXT
);

CREATE TABLE PACIENTE (
    id_pessoa INTEGER PRIMARY KEY,
    num_convenio TEXT,
    alergias TEXT,
    grupo_sanguineo TEXT CHECK (grupo_sanguineo IN
                        ('A+','A-','B+','B-','AB+','AB-','O+','O-')),
    FOREIGN KEY (id_pessoa) REFERENCES PESSOA(id_pessoa)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE PROFISSIONAL (
    id_pessoa INTEGER PRIMARY KEY,
    crm TEXT NOT NULL UNIQUE,
    data_admissao DATE NOT NULL,
    especialidade TEXT NOT NULL,
    FOREIGN KEY (id_pessoa) REFERENCES PESSOA(id_pessoa)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE PRECEPTOR (
    id_profissional INTEGER PRIMARY KEY,
    titulacao TEXT NOT NULL CHECK (titulacao IN
                        ('especialista','mestre','doutor','livre-docente')),
    FOREIGN KEY (id_profissional) REFERENCES PROFISSIONAL(id_pessoa)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE RESIDENTE (
    id_profissional INTEGER PRIMARY KEY,
    ano_residencia TEXT NOT NULL CHECK (ano_residencia IN ('R1','R2','R3')),
    FOREIGN KEY (id_profissional) REFERENCES PROFISSIONAL(id_pessoa)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE UNIDADE (
    id_unidade SERIAL PRIMARY KEY,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK (tipo IN
                          ('Enfermaria','UTI','Pronto-Socorro','Ambulatorio')),
    capacidade_leitos INTEGER NOT NULL CHECK (capacidade_leitos >= 0)
);

CREATE TABLE ATENDIMENTO (
    id_atendimento SERIAL PRIMARY KEY,
    data_hora TIMESTAMP NOT NULL,
    duracao_minutos INTEGER NOT NULL CHECK (duracao_minutos > 0),
    id_paciente INTEGER NOT NULL,
    id_residente INTEGER NOT NULL,
    id_preceptor INTEGER NOT NULL,
    id_unidade INTEGER,
    FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_pessoa),
    FOREIGN KEY (id_residente) REFERENCES RESIDENTE(id_profissional),
    FOREIGN KEY (id_preceptor) REFERENCES PRECEPTOR(id_profissional),
    FOREIGN KEY (id_unidade) REFERENCES UNIDADE(id_unidade)
);

CREATE TABLE PROCEDIMENTO (
    id_procedimento SERIAL PRIMARY KEY,
    codigo TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    tempo_medio_minutos INTEGER NOT NULL CHECK (tempo_medio_minutos > 0),
    nivel_risco TEXT NOT NULL DEFAULT 'BAIXO'
                            CHECK (nivel_risco IN ('BAIXO','MEDIO','ALTO')),
    media_tempo_procedimento NUMERIC(8,2) DEFAULT NULL
);

CREATE TABLE PROCEDIMENTO_REALIZADO (
    id_atendimento INTEGER NOT NULL,
    id_procedimento INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    tempo_real_minutos INTEGER NOT NULL CHECK (tempo_real_minutos > 0),
    observacao TEXT,
    faturado INTEGER NOT NULL DEFAULT 0 CHECK (faturado IN (0,1)),
    PRIMARY KEY (id_atendimento, id_procedimento),
    FOREIGN KEY (id_atendimento) REFERENCES ATENDIMENTO(id_atendimento)
        ON DELETE CASCADE,
    FOREIGN KEY (id_procedimento) REFERENCES PROCEDIMENTO(id_procedimento)
);

CREATE TABLE ESCALA (
    id_escala SERIAL PRIMARY KEY,
    id_unidade INTEGER NOT NULL,
    dia_semana TEXT NOT NULL CHECK (dia_semana IN
                     ('segunda','terca','quarta','quinta','sexta','sabado','domingo')),
    turno TEXT NOT NULL CHECK (turno IN ('manha','tarde','noite')),
    id_residente INTEGER NOT NULL,
    id_preceptor INTEGER NOT NULL,
    FOREIGN KEY (id_unidade) REFERENCES UNIDADE(id_unidade),
    FOREIGN KEY (id_residente) REFERENCES RESIDENTE(id_profissional),
    FOREIGN KEY (id_preceptor) REFERENCES PRECEPTOR(id_profissional),
    UNIQUE (id_unidade, dia_semana, turno, id_residente)
);

CREATE TABLE INTERNACAO (
    id_internacao SERIAL PRIMARY KEY,
    id_paciente   INTEGER NOT NULL,
    id_unidade    INTEGER NOT NULL,
    data_entrada  TIMESTAMP NOT NULL,
    data_saida    TIMESTAMP,
    FOREIGN KEY (id_paciente) REFERENCES PACIENTE(id_pessoa) ON DELETE CASCADE,
    FOREIGN KEY (id_unidade) REFERENCES UNIDADE(id_unidade)
);

CREATE TABLE AUDITORIA_ATENDIMENTO (
    id_auditoria   SERIAL PRIMARY KEY,
    id_atendimento INTEGER,
    operacao       TEXT NOT NULL CHECK (operacao IN ('INSERT','UPDATE','DELETE')),
    usuario        TEXT NOT NULL,
    data_hora      TIMESTAMP NOT NULL DEFAULT NOW(),
    dados_antigos  JSONB,
    dados_novos    JSONB
);

CREATE INDEX idx_atendimento_residente ON ATENDIMENTO(id_residente);
CREATE INDEX idx_atendimento_preceptor ON ATENDIMENTO(id_preceptor);
CREATE INDEX idx_atendimento_data ON ATENDIMENTO(data_hora);
CREATE INDEX idx_atendimento_unidade ON ATENDIMENTO(id_unidade);
CREATE INDEX idx_escala_unidade_res ON ESCALA(id_unidade, id_residente);
CREATE INDEX idx_internacao_paciente ON INTERNACAO(id_paciente);
