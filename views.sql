CREATE OR REPLACE VIEW vw_pacientes_internados AS
SELECT
    p.id_pessoa,
    p.nome,
    i.data_entrada,
    u.nome AS unidade
FROM INTERNACAO i
JOIN PESSOA p ON p.id_pessoa = i.id_paciente
JOIN UNIDADE u ON u.id_unidade = i.id_unidade
WHERE i.data_saida IS NULL
  AND i.id_internacao = (
      SELECT MAX(i2.id_internacao)
      FROM INTERNACAO i2
      WHERE i2.id_paciente = i.id_paciente
  );


CREATE OR REPLACE VIEW vw_residentes_sem_supervisor AS
SELECT DISTINCT
    p_res.nome    AS residente,
    p_prec.nome   AS preceptor,
    prec.titulacao
FROM ESCALA e
JOIN PESSOA p_res   ON p_res.id_pessoa   = e.id_residente
JOIN PRECEPTOR prec ON prec.id_profissional = e.id_preceptor
JOIN PESSOA p_prec  ON p_prec.id_pessoa  = e.id_preceptor
WHERE prec.titulacao != 'doutor';


CREATE OR REPLACE VIEW vw_estatisticas_atendimentos_mensal AS
SELECT
    DATE_TRUNC('month', a.data_hora)          AS mes,
    u.nome                                    AS unidade,
    COUNT(DISTINCT a.id_atendimento)          AS total_atendimentos,
    ROUND(AVG(a.duracao_minutos)::NUMERIC, 2) AS media_duracao_min,
    MODE() WITHIN GROUP (ORDER BY p.nome)     AS procedimento_mais_comum
FROM ATENDIMENTO a
JOIN UNIDADE u  ON u.id_unidade  = a.id_unidade
JOIN PROCEDIMENTO_REALIZADO pr ON pr.id_atendimento = a.id_atendimento
JOIN PROCEDIMENTO p ON p.id_procedimento = pr.id_procedimento
GROUP BY DATE_TRUNC('month', a.data_hora), u.id_unidade, u.nome
ORDER BY mes, unidade;
