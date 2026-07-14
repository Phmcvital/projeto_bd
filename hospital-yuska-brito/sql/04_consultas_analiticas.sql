-- Consultas Analiticas (Etapa 4) -- Sistema de Gestao Hospitalar
-- Banco: PostgreSQL | SQL puro (sem ORM)


-- 1. Ranking dos residentes pelo numero de atendimentos realizados
-- O LEFT JOIN mantem no ranking residentes que ainda nao fizeram atendimentos.

SELECT
    DENSE_RANK() OVER (ORDER BY COUNT(a.id_atendimento) DESC) AS posicao,
    p.nome                                                    AS residente,
    COUNT(a.id_atendimento)                                  AS total_atendimentos
FROM RESIDENTE r
JOIN PESSOA p
    ON p.id_pessoa = r.id_profissional
LEFT JOIN ATENDIMENTO a
    ON a.id_residente = r.id_profissional
GROUP BY r.id_profissional, p.nome
ORDER BY posicao, residente;


-- 2. Preceptores que supervisionaram mais de 5 atendimentos em um mes
-- Altere somente mes_referencia para consultar outro mes. O intervalo
-- semiaberto considera o ano e evita problemas com o horario do atendimento.

WITH parametros AS (
    SELECT DATE '2025-06-01' AS mes_referencia
)
SELECT
    p.nome                   AS preceptor,
    COUNT(a.id_atendimento) AS total_atendimentos
FROM parametros prm
JOIN ATENDIMENTO a
    ON a.data_hora >= prm.mes_referencia
   AND a.data_hora <  prm.mes_referencia + INTERVAL '1 month'
JOIN PRECEPTOR pre
    ON pre.id_profissional = a.id_preceptor
JOIN PESSOA p
    ON p.id_pessoa = pre.id_profissional
GROUP BY pre.id_profissional, p.nome
HAVING COUNT(a.id_atendimento) > 5
ORDER BY total_atendimentos DESC, preceptor;


-- 3. Quantidade de plantoes por residente e unidade no mes corrente
-- Como ESCALA armazena um dia da semana (escala semanal recorrente), os dias
-- reais do mes corrente sao gerados e associados a cada recorrencia cadastrada.

WITH limites_mes AS (
    SELECT
        DATE_TRUNC('month', CURRENT_DATE)::DATE AS inicio_mes,
        (DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month')::DATE AS fim_mes
),
dias_do_mes AS (
    SELECT
        gs.data_plantao::DATE AS data_plantao,
        CASE EXTRACT(ISODOW FROM gs.data_plantao)::INTEGER
            WHEN 1 THEN 'segunda'
            WHEN 2 THEN 'terca'
            WHEN 3 THEN 'quarta'
            WHEN 4 THEN 'quinta'
            WHEN 5 THEN 'sexta'
            WHEN 6 THEN 'sabado'
            WHEN 7 THEN 'domingo'
        END AS dia_semana
    FROM limites_mes lm
    CROSS JOIN LATERAL GENERATE_SERIES(
        lm.inicio_mes,
        lm.fim_mes - 1,
        INTERVAL '1 day'
    ) AS gs(data_plantao)
)
SELECT
    u.nome   AS unidade,
    p.nome   AS residente,
    COUNT(*) AS total_plantoes
FROM ESCALA e
JOIN dias_do_mes dm
    ON dm.dia_semana = e.dia_semana
JOIN UNIDADE u
    ON u.id_unidade = e.id_unidade
JOIN RESIDENTE r
    ON r.id_profissional = e.id_residente
JOIN PESSOA p
    ON p.id_pessoa = r.id_profissional
GROUP BY u.id_unidade, u.nome, r.id_profissional, p.nome
ORDER BY unidade, total_plantoes DESC, residente;


-- 4. Pacientes que nunca realizaram procedimento de risco ALTO
-- NOT EXISTS tambem inclui pacientes que ainda nao realizaram procedimento.

SELECT
    p.nome AS paciente
FROM PACIENTE pac
JOIN PESSOA p
    ON p.id_pessoa = pac.id_pessoa
WHERE NOT EXISTS (
    SELECT 1
    FROM ATENDIMENTO a
    JOIN PROCEDIMENTO_REALIZADO pr
        ON pr.id_atendimento = a.id_atendimento
    JOIN PROCEDIMENTO proc
        ON proc.id_procedimento = pr.id_procedimento
    WHERE a.id_paciente = pac.id_pessoa
      AND proc.nivel_risco = 'ALTO'
)
ORDER BY paciente;
