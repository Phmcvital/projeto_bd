-- Demonstracoes manuais da Etapa 2
-- Execute depois de: python db.py

-- 1. Atendimento completo. O ROLLBACK deixa os dados de seed intactos.
BEGIN;
CALL sp_registrar_atendimento_completo(
    '2026-08-02 10:00:00',
    40,
    1,
    11,
    6,
    1,
    '[
        {
            "id_procedimento": 1,
            "quantidade": 1,
            "data_hora_inicio": "2026-08-02 10:08:00",
            "tempo_real_minutos": 21,
            "observacao": "Teste da procedure",
            "faturado": false
        },
        {
            "id_procedimento": 2,
            "quantidade": 1,
            "data_hora_inicio": "2026-08-02 10:30:00",
            "tempo_real_minutos": 9,
            "observacao": "Segundo procedimento",
            "faturado": false
        }
    ]'::JSONB
);
SELECT * FROM ATENDIMENTO ORDER BY id_atendimento DESC LIMIT 1;
ROLLBACK;

-- Para testar o rollback automatico, troque id_procedimento por 999.
-- O atendimento tambem nao sera gravado por causa da chave estrangeira invalida.


-- 2. Tempo medio de espera por unidade.
CALL sp_calcular_tempo_medio_espera();
SELECT * FROM resultado_tempo_medio_espera;


-- 3. Reajuste de escala dentro de uma transacao de teste.
BEGIN;
CALL sp_reajustar_escala(11, 'segunda', 'manha', 'domingo', 'tarde');
SELECT * FROM ESCALA WHERE id_residente = 11;
ROLLBACK;


-- 4. Views.
SELECT * FROM vw_pacientes_internados;
SELECT * FROM vw_residentes_sem_supervisor;
SELECT * FROM vw_estatisticas_atendimentos_mensal;


-- 5. Triggers.
SELECT * FROM AUDITORIA_ATENDIMENTO ORDER BY id_auditoria DESC;
SELECT id_procedimento, nome, media_tempo_procedimento FROM PROCEDIMENTO;

-- Este INSERT deve falhar porque o residente 11 ja esta na segunda/manha
-- na unidade 1:
-- INSERT INTO ESCALA
--     (id_unidade, dia_semana, turno, id_residente, id_preceptor)
-- VALUES (2, 'segunda', 'manha', 11, 6);
