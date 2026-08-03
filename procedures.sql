-- sp_registrar_atendimento_completo
CREATE OR REPLACE FUNCTION sp_registrar_atendimento_completo(
    p_data_hora        TIMESTAMP,
    p_duracao_minutos  INTEGER,
    p_id_paciente      INTEGER,
    p_id_residente     INTEGER,
    p_id_preceptor     INTEGER,
    p_id_unidade       INTEGER,
    p_procedimentos    JSON
) RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_atendimento INTEGER;
    v_proc           JSON;
BEGIN
    INSERT INTO ATENDIMENTO (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade)
    VALUES (p_data_hora, p_duracao_minutos, p_id_paciente, p_id_residente, p_id_preceptor, p_id_unidade)
    RETURNING id_atendimento INTO v_id_atendimento;

    FOR v_proc IN SELECT * FROM json_array_elements(p_procedimentos)
    LOOP
        INSERT INTO PROCEDIMENTO_REALIZADO
            (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao)
        VALUES (
            v_id_atendimento,
            (v_proc->>'id_procedimento')::INTEGER,
            (v_proc->>'quantidade')::INTEGER,
            (v_proc->>'tempo_real_minutos')::INTEGER,
            v_proc->>'observacao'
        );
    END LOOP;

    RETURN v_id_atendimento;
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$$;


-- sp_calcular_tempo_medio_espera
CREATE OR REPLACE FUNCTION sp_calcular_tempo_medio_espera()
RETURNS TABLE(id_unidade INTEGER, nome_unidade TEXT, tempo_medio_minutos NUMERIC)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id_unidade,
        u.nome::TEXT,
        ROUND(AVG(primeiro.tempo_real_minutos)::NUMERIC, 2)
    FROM UNIDADE u
    JOIN ATENDIMENTO a ON a.id_unidade = u.id_unidade
    JOIN (
        SELECT DISTINCT ON (pr.id_atendimento)
            pr.id_atendimento,
            pr.tempo_real_minutos
        FROM PROCEDIMENTO_REALIZADO pr
        ORDER BY pr.id_atendimento, pr.id_procedimento ASC
    ) primeiro ON primeiro.id_atendimento = a.id_atendimento
    GROUP BY u.id_unidade, u.nome
    ORDER BY u.nome;
END;
$$;


-- sp_reajustar_escala
CREATE OR REPLACE FUNCTION sp_reajustar_escala(
    p_id_residente  INTEGER,
    p_dia_origem    TEXT,
    p_turno_origem  TEXT,
    p_dia_destino   TEXT,
    p_turno_destino TEXT
) RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_escala RECORD;
    v_count  INTEGER := 0;
BEGIN
    FOR v_escala IN
        SELECT id_escala, id_unidade
        FROM ESCALA
        WHERE id_residente = p_id_residente
          AND dia_semana = p_dia_origem
          AND turno = p_turno_origem
    LOOP
        -- Conflito na mesma unidade no destino
        IF EXISTS (
            SELECT 1 FROM ESCALA
            WHERE id_residente = p_id_residente
              AND id_unidade = v_escala.id_unidade
              AND dia_semana = p_dia_destino
              AND turno = p_turno_destino
              AND id_escala != v_escala.id_escala
        ) THEN
            RAISE EXCEPTION 'Conflito: residente % ja escalado na unidade % no dia % turno %',
                p_id_residente, v_escala.id_unidade, p_dia_destino, p_turno_destino;
        END IF;

        -- Conflito em outra unidade no mesmo dia/turno destino
        IF EXISTS (
            SELECT 1 FROM ESCALA
            WHERE id_residente = p_id_residente
              AND id_unidade != v_escala.id_unidade
              AND dia_semana = p_dia_destino
              AND turno = p_turno_destino
        ) THEN
            RAISE EXCEPTION 'Conflito: residente % ja escalado no dia % turno % em outra unidade',
                p_id_residente, p_dia_destino, p_turno_destino;
        END IF;

        UPDATE ESCALA
        SET dia_semana = p_dia_destino, turno = p_turno_destino
        WHERE id_escala = v_escala.id_escala;

        v_count := v_count + 1;
    END LOOP;

    IF v_count = 0 THEN
        RAISE EXCEPTION 'Nenhuma escala encontrada para residente % no dia % turno %',
            p_id_residente, p_dia_origem, p_turno_origem;
    END IF;

    RETURN v_count;
END;
$$;
