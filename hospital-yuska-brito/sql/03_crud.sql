-- CRUD e Consultas Básicas — Sistema de Gestão Hospitalar
-- Banco: PostgreSQL | SQL puro (sem ORM)


-- INSERT — Procedure: inserir novo atendimento com verificação de existência

CREATE OR REPLACE PROCEDURE inserir_atendimento(
    p_id_paciente  INTEGER,
    p_id_residente INTEGER,
    p_id_preceptor INTEGER,
    p_id_unidade   INTEGER,
    p_data_hora    TIMESTAMP,
    p_duracao      NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM PACIENTE  WHERE id_pessoa       = p_id_paciente)  THEN
        RAISE EXCEPTION 'Paciente com id % nao encontrado.',  p_id_paciente;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM RESIDENTE WHERE id_profissional = p_id_residente) THEN
        RAISE EXCEPTION 'Residente com id % nao encontrado.', p_id_residente;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM PRECEPTOR WHERE id_profissional = p_id_preceptor) THEN
        RAISE EXCEPTION 'Preceptor com id % nao encontrado.', p_id_preceptor;
    END IF;

    INSERT INTO ATENDIMENTO (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade)
    VALUES (p_data_hora, p_duracao, p_id_paciente, p_id_residente, p_id_preceptor, p_id_unidade);

    RAISE NOTICE 'Atendimento inserido com sucesso.';
END;
$$;

-- Exemplo de uso:
CALL inserir_atendimento(3, 8, 12, 2, '2026-07-10 09:00:00', 45.0);



-- SELECT — Todos os atendimentos de um paciente (por data)
-- Troque o valor de id_paciente conforme necessário.

SELECT
    a.id_atendimento,
    a.data_hora,
    a.duracao_minutos,
    pac.nome      AS paciente,
    res.nome      AS residente,
    pre.nome      AS preceptor,
    u.nome        AS unidade
FROM ATENDIMENTO a
JOIN PESSOA  pac ON pac.id_pessoa       = a.id_paciente
JOIN PESSOA  res ON res.id_pessoa       = a.id_residente
JOIN PESSOA  pre ON pre.id_pessoa       = a.id_preceptor
JOIN UNIDADE u   ON u.id_unidade        = a.id_unidade
WHERE a.id_paciente = 1
ORDER BY a.data_hora;


-- SELECT — Procedimentos realizados em um atendimento
-- Troque o valor de id_atendimento conforme necessário.

SELECT
    p.codigo,
    p.nome                 AS procedimento,
    pr.quantidade,
    pr.tempo_real_minutos,
    pr.observacao
FROM PROCEDIMENTO_REALIZADO pr
JOIN PROCEDIMENTO p ON p.id_procedimento = pr.id_procedimento
WHERE pr.id_atendimento = 3
ORDER BY p.nome;



-- UPDATE — Dados de um paciente (número de convênio)
-- Troque o id e o novo valor conforme necessário.

UPDATE PACIENTE
SET num_convenio = 'SULAMERICA-999'
WHERE id_pessoa = 2;

-- Confirmação
SELECT id_pessoa, num_convenio, alergias, grupo_sanguineo
FROM PACIENTE
WHERE id_pessoa = 2;



-- DELETE — Procedimento realizado (apenas se não faturado)
-- Troque os ids conforme necessário.

DELETE FROM PROCEDIMENTO_REALIZADO
WHERE id_atendimento  = 2
  AND id_procedimento = 2
  AND faturado = FALSE;

-- Confirmação: deve retornar 0 linhas se deletado com sucesso
SELECT * FROM PROCEDIMENTO_REALIZADO
WHERE id_atendimento = 2 AND id_procedimento = 2;



-- SELECT — Tempo médio de duração dos atendimentos por residente

SELECT
    p.nome                               AS residente,
    r.ano_residencia,
    COUNT(a.id_atendimento)              AS total_atendimentos,
    ROUND(AVG(a.duracao_minutos), 2)     AS media_duracao_minutos
FROM ATENDIMENTO a
JOIN RESIDENTE r ON r.id_profissional = a.id_residente
JOIN PESSOA    p ON p.id_pessoa       = a.id_residente
GROUP BY a.id_residente, p.nome, r.ano_residencia
ORDER BY media_duracao_minutos DESC;
