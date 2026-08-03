-- Etapa 2 - Procedures, triggers e views
-- PostgreSQL / PL/pgSQL

-- ============================================================
-- 1. TRIGGERS
-- ============================================================

-- Impede que um residente esteja no mesmo dia/turno em duas unidades.
CREATE OR REPLACE FUNCTION fn_check_sobreposicao_escala()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM ESCALA e
        WHERE e.id_residente = NEW.id_residente
          AND e.dia_semana = NEW.dia_semana
          AND e.turno = NEW.turno
          AND e.id_unidade <> NEW.id_unidade
          AND e.id_escala <> COALESCE(NEW.id_escala, -1)
    ) THEN
        RAISE EXCEPTION
            'O residente % ja esta escalado em outra unidade nesse dia e turno.',
            NEW.id_residente;
    END IF;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_check_sobreposicao_escala
BEFORE INSERT OR UPDATE ON ESCALA
FOR EACH ROW
EXECUTE FUNCTION fn_check_sobreposicao_escala();


-- Registra todas as alteracoes feitas em ATENDIMENTO.
CREATE OR REPLACE FUNCTION fn_audita_atendimento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO AUDITORIA_ATENDIMENTO
            (id_atendimento, operacao, usuario, dados_antigos, dados_novos)
        VALUES
            (NEW.id_atendimento, TG_OP, CURRENT_USER, NULL, TO_JSONB(NEW));
        RETURN NEW;

    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO AUDITORIA_ATENDIMENTO
            (id_atendimento, operacao, usuario, dados_antigos, dados_novos)
        VALUES
            (NEW.id_atendimento, TG_OP, CURRENT_USER, TO_JSONB(OLD), TO_JSONB(NEW));
        RETURN NEW;

    ELSE
        INSERT INTO AUDITORIA_ATENDIMENTO
            (id_atendimento, operacao, usuario, dados_antigos, dados_novos)
        VALUES
            (OLD.id_atendimento, TG_OP, CURRENT_USER, TO_JSONB(OLD), NULL);
        RETURN OLD;
    END IF;
END;
$$;

CREATE TRIGGER trg_audita_atendimento
AFTER INSERT OR UPDATE OR DELETE ON ATENDIMENTO
FOR EACH ROW
EXECUTE FUNCTION fn_audita_atendimento();


-- Recalcula a media real do procedimento inserido.
CREATE OR REPLACE FUNCTION fn_atualiza_media_procedimento()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE PROCEDIMENTO
    SET media_tempo_procedimento = (
        SELECT ROUND(AVG(pr.tempo_real_minutos)::NUMERIC, 2)
        FROM PROCEDIMENTO_REALIZADO pr
        WHERE pr.id_procedimento = NEW.id_procedimento
    )
    WHERE id_procedimento = NEW.id_procedimento;

    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_atualiza_media_procedimentos
AFTER INSERT ON PROCEDIMENTO_REALIZADO
FOR EACH ROW
EXECUTE FUNCTION fn_atualiza_media_procedimento();


-- ============================================================
-- 2. STORED PROCEDURES
-- ============================================================

-- Exemplo do JSON recebido em p_procedimentos:
-- [
--   {
--     "id_procedimento": 1,
--     "quantidade": 1,
--     "data_hora_inicio": "2026-08-02 10:10:00",
--     "tempo_real_minutos": 20,
--     "observacao": "Sem intercorrencias",
--     "faturado": false
--   }
-- ]
CREATE OR REPLACE PROCEDURE sp_registrar_atendimento_completo(
    p_data_hora TIMESTAMP,
    p_duracao_minutos INTEGER,
    p_id_paciente INTEGER,
    p_id_residente INTEGER,
    p_id_preceptor INTEGER,
    p_id_unidade INTEGER,
    p_procedimentos JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_atendimento INTEGER;
    v_item JSONB;
BEGIN
    IF JSONB_TYPEOF(p_procedimentos) IS DISTINCT FROM 'array'
       OR JSONB_ARRAY_LENGTH(p_procedimentos) = 0 THEN
        RAISE EXCEPTION 'A lista de procedimentos deve ser um JSON nao vazio.';
    END IF;

    INSERT INTO ATENDIMENTO
        (data_hora, duracao_minutos, id_paciente, id_residente,
         id_preceptor, id_unidade)
    VALUES
        (p_data_hora, p_duracao_minutos, p_id_paciente, p_id_residente,
         p_id_preceptor, p_id_unidade)
    RETURNING id_atendimento INTO v_id_atendimento;

    FOR v_item IN
        SELECT value FROM JSONB_ARRAY_ELEMENTS(p_procedimentos)
    LOOP
        INSERT INTO PROCEDIMENTO_REALIZADO
            (id_atendimento, id_procedimento, quantidade,
             data_hora_inicio, tempo_real_minutos, observacao, faturado)
        VALUES
            (v_id_atendimento,
             (v_item ->> 'id_procedimento')::INTEGER,
             COALESCE((v_item ->> 'quantidade')::INTEGER, 1),
             COALESCE((v_item ->> 'data_hora_inicio')::TIMESTAMP, p_data_hora),
             (v_item ->> 'tempo_real_minutos')::INTEGER,
             v_item ->> 'observacao',
             COALESCE((v_item ->> 'faturado')::BOOLEAN, FALSE));
    END LOOP;

    RAISE NOTICE 'Atendimento % e procedimentos registrados.', v_id_atendimento;
    -- Se qualquer INSERT falhar, a chamada inteira e desfeita pelo PostgreSQL.
END;
$$;


-- O resultado e colocado em uma tabela temporaria da sessao.
-- Apos o CALL, execute: SELECT * FROM resultado_tempo_medio_espera;
CREATE OR REPLACE PROCEDURE sp_calcular_tempo_medio_espera()
LANGUAGE plpgsql
AS $$
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS resultado_tempo_medio_espera (
        id_unidade INTEGER,
        unidade VARCHAR(100),
        total_atendimentos BIGINT,
        media_espera_minutos NUMERIC(10,2)
    ) ON COMMIT PRESERVE ROWS;

    TRUNCATE TABLE resultado_tempo_medio_espera;

    INSERT INTO resultado_tempo_medio_espera
        (id_unidade, unidade, total_atendimentos, media_espera_minutos)
    SELECT
        u.id_unidade,
        u.nome,
        COUNT(*),
        ROUND(AVG(EXTRACT(EPOCH FROM
            (primeiro.inicio_procedimento - primeiro.chegada)) / 60)::NUMERIC, 2)
    FROM (
        SELECT
            a.id_atendimento,
            a.id_unidade,
            a.data_hora AS chegada,
            MIN(pr.data_hora_inicio) AS inicio_procedimento
        FROM ATENDIMENTO a
        JOIN PROCEDIMENTO_REALIZADO pr
            ON pr.id_atendimento = a.id_atendimento
        GROUP BY a.id_atendimento, a.id_unidade, a.data_hora
    ) primeiro
    JOIN UNIDADE u ON u.id_unidade = primeiro.id_unidade
    GROUP BY u.id_unidade, u.nome
    ORDER BY u.nome;
END;
$$;


CREATE OR REPLACE PROCEDURE sp_reajustar_escala(
    p_id_residente INTEGER,
    p_dia_origem VARCHAR(10),
    p_turno_origem VARCHAR(5),
    p_dia_destino VARCHAR(10),
    p_turno_destino VARCHAR(5)
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_total INTEGER;
BEGIN
    IF p_dia_destino NOT IN
       ('segunda','terca','quarta','quinta','sexta','sabado','domingo') THEN
        RAISE EXCEPTION 'Dia de destino invalido: %.', p_dia_destino;
    END IF;

    IF p_turno_destino NOT IN ('manha','tarde','noite') THEN
        RAISE EXCEPTION 'Turno de destino invalido: %.', p_turno_destino;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM ESCALA
        WHERE id_residente = p_id_residente
          AND dia_semana = p_dia_origem
          AND turno = p_turno_origem
    ) THEN
        RAISE EXCEPTION 'Nenhuma escala de origem foi encontrada.';
    END IF;

    IF EXISTS (
        SELECT 1
        FROM ESCALA origem
        JOIN ESCALA destino
          ON destino.id_unidade = origem.id_unidade
         AND destino.id_residente = origem.id_residente
         AND destino.dia_semana = p_dia_destino
         AND destino.turno = p_turno_destino
         AND destino.id_escala <> origem.id_escala
        WHERE origem.id_residente = p_id_residente
          AND origem.dia_semana = p_dia_origem
          AND origem.turno = p_turno_origem
    ) THEN
        RAISE EXCEPTION
            'Reajuste cancelado: ja existe escala do residente no destino.';
    END IF;

    UPDATE ESCALA
    SET dia_semana = p_dia_destino,
        turno = p_turno_destino
    WHERE id_residente = p_id_residente
      AND dia_semana = p_dia_origem
      AND turno = p_turno_origem;

    GET DIAGNOSTICS v_total = ROW_COUNT;
    RAISE NOTICE '% escala(s) reajustada(s).', v_total;
END;
$$;


-- ============================================================
-- 3. VIEWS
-- ============================================================

CREATE OR REPLACE VIEW vw_pacientes_internados AS
SELECT
    i.id_internacao,
    pac.id_pessoa AS id_paciente,
    pes.nome AS paciente,
    u.id_unidade,
    u.nome AS unidade,
    i.data_hora_entrada
FROM INTERNACAO i
JOIN PACIENTE pac ON pac.id_pessoa = i.id_paciente
JOIN PESSOA pes ON pes.id_pessoa = pac.id_pessoa
JOIN UNIDADE u ON u.id_unidade = i.id_unidade
WHERE i.data_hora_saida IS NULL
  AND NOT EXISTS (
      SELECT 1
      FROM INTERNACAO mais_recente
      WHERE mais_recente.id_paciente = i.id_paciente
        AND mais_recente.data_hora_entrada > i.data_hora_entrada
  );


CREATE OR REPLACE VIEW vw_residentes_sem_supervisor AS
SELECT
    e.id_escala,
    r.id_profissional AS id_residente,
    pessoa_residente.nome AS residente,
    u.nome AS unidade,
    e.dia_semana,
    e.turno,
    pessoa_preceptor.nome AS preceptor,
    pre.titulacao
FROM ESCALA e
JOIN RESIDENTE r ON r.id_profissional = e.id_residente
JOIN PESSOA pessoa_residente
    ON pessoa_residente.id_pessoa = r.id_profissional
JOIN UNIDADE u ON u.id_unidade = e.id_unidade
LEFT JOIN PRECEPTOR pre ON pre.id_profissional = e.id_preceptor
LEFT JOIN PESSOA pessoa_preceptor
    ON pessoa_preceptor.id_pessoa = pre.id_profissional
WHERE pre.id_profissional IS NULL
   OR pre.titulacao <> 'doutor';


CREATE OR REPLACE VIEW vw_estatisticas_atendimentos_mensal AS
WITH resumo AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        COUNT(*) AS total_atendimentos,
        ROUND(AVG(a.duracao_minutos)::NUMERIC, 2) AS media_duracao_minutos
    FROM ATENDIMENTO a
    GROUP BY DATE_TRUNC('month', a.data_hora)::DATE, a.id_unidade
),
quantidade_procedimentos AS (
    SELECT
        DATE_TRUNC('month', a.data_hora)::DATE AS mes,
        a.id_unidade,
        p.nome AS procedimento,
        SUM(pr.quantidade) AS quantidade,
        ROW_NUMBER() OVER (
            PARTITION BY DATE_TRUNC('month', a.data_hora)::DATE, a.id_unidade
            ORDER BY SUM(pr.quantidade) DESC, p.nome
        ) AS posicao
    FROM ATENDIMENTO a
    JOIN PROCEDIMENTO_REALIZADO pr
        ON pr.id_atendimento = a.id_atendimento
    JOIN PROCEDIMENTO p
        ON p.id_procedimento = pr.id_procedimento
    GROUP BY DATE_TRUNC('month', a.data_hora)::DATE, a.id_unidade, p.nome
)
SELECT
    r.mes,
    u.id_unidade,
    u.nome AS unidade,
    r.total_atendimentos,
    r.media_duracao_minutos,
    qp.procedimento AS procedimento_mais_comum,
    qp.quantidade AS quantidade_procedimento
FROM resumo r
JOIN UNIDADE u ON u.id_unidade = r.id_unidade
LEFT JOIN quantidade_procedimentos qp
    ON qp.mes = r.mes
   AND qp.id_unidade = r.id_unidade
   AND qp.posicao = 1;
