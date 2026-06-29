-- DML: Dados de teste — Sistema de Gestão Hospitalar

BEGIN;

-- PESSOAS (5 pacientes + 5 residentes + 5 preceptores = 15)
INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
-- pacientes: elenco atual 2025/2026 (id 1-5)
('Gerson Santos de Oliveira',    '98412376501', '1997-05-20', TRUE, '(21) 98412-3765'),
('Giorgian De Arrascaeta',       '74523891204', '1994-06-01', TRUE, '(22) 97523-8912'),
('Nicolas De La Cruz',           '63148927305', '1997-06-01', TRUE, '(11) 99148-9273'),
('Leonardo Ortiz',               '52736184906', '1996-01-18', TRUE, '(21) 98736-1849'),
('Erick Pulgar',                 '41925837107', '1994-01-15', TRUE, '(22) 97925-8371'),
-- residentes: melhores do elenco de 2019 (id 6-10)
('Gabriel Barbosa',              '87614392508', '1996-08-30', TRUE, '(21) 98614-3925'),
('Everton Ribeiro de Souza',     '76523841209', '1989-01-02', TRUE, '(11) 97652-3841'),
('Bruno Henrique Pinto',         '65412783910', '1990-10-27', TRUE, '(21) 98541-2783'),
('Filipe Luis Kasmirski',        '54891632711', '1988-08-09', TRUE, '(22) 97489-1632'),
('Diego Ribas da Cunha',         '43782591412', '1985-02-28', TRUE, '(21) 98378-2591'),
-- preceptores: campeoes mundiais de 1981 (id 11-15)
('Arthur Antunes Coimbra',       '32671489513', '1953-03-03', TRUE, '(11) 97267-1489'),
('Marcos Antonio Batista Junior','21594378614', '1954-06-29', TRUE, '(22) 98159-4378'),
('Adilio Pereira de Carvalho',   '19483267715', '1955-05-17', TRUE, '(21) 97948-3267'),
('Paulo Cesar Nunes',            '98372156816', '1956-07-10', TRUE, '(11) 98837-2156'),
('Leandro Bastos Iorio',         '87261945917', '1954-09-29', TRUE, '(22) 97726-1945');

-- PACIENTES
INSERT INTO PACIENTE (id_pessoa, num_convenio, alergias, grupo_sanguineo) VALUES
(1, 'UNIMED-001',   'Penicilina',           'A+'),
(2, NULL,           NULL,                   'B-'),
(3, 'BRADESCO-033', 'Dipirona, Latex',      'O+'),
(4, 'AMIL-444',     NULL,                   'AB+'),
(5, NULL,           'AAS',                  'A-');

-- PROFISSIONAIS (residentes + preceptores)
INSERT INTO PROFISSIONAL (id_pessoa, crm, data_admissao, especialidade) VALUES
(6,  'CRM/RJ-100006', '2022-03-01', 'Clinica Medica'),
(7,  'CRM/RJ-100007', '2021-08-15', 'Cirurgia Geral'),
(8,  'CRM/RJ-100008', '2023-01-10', 'Cardiologia'),
(9,  'CRM/RJ-100009', '2022-07-20', 'Neurologia'),
(10, 'CRM/RJ-100010', '2023-06-01', 'Ortopedia'),
(11, 'CRM/RJ-200011', '2010-05-10', 'Clinica Medica'),
(12, 'CRM/RJ-200012', '2008-09-22', 'Cirurgia Geral'),
(13, 'CRM/RJ-200013', '2012-11-30', 'Cardiologia'),
(14, 'CRM/RJ-200014', '2005-03-14', 'Neurologia'),
(15, 'CRM/RJ-200015', '2009-07-01', 'Ortopedia');

-- RESIDENTES (melhores de 2019)
INSERT INTO RESIDENTE (id_profissional, ano_residencia) VALUES
(6,  '2022'),
(7,  '2021'),
(8,  '2023'),
(9,  '2022'),
(10, '2023');

-- PRECEPTORES (campeoes de 1981)
INSERT INTO PRECEPTOR (id_profissional, titulacao) VALUES
(11, 'Doutor'),
(12, 'Mestre'),
(13, 'Doutor'),
(14, 'Especialista'),
(15, 'Mestre');

-- UNIDADES
INSERT INTO UNIDADE (nome, capacidade_leitos) VALUES
('UTI Geral',      20),
('Pronto-Socorro', 30),
('Ambulatorio',    50);

-- PROCEDIMENTOS
INSERT INTO PROCEDIMENTO (nome, nivel_risco, tempo_estimado_minutos) VALUES
('Endoscopia Diagnostica',     'BAIXO',  30),
('Tomografia Computadorizada', 'MEDIO',  45),
('Cirurgia Laparoscopica',     'ALTO',  120),
('Cateterismo Cardiaco',       'ALTO',   90),
('Coleta de Sangue',           'BAIXO',  10),
('Hemodialise',                'MEDIO', 240);

-- ATENDIMENTOS (10)
INSERT INTO ATENDIMENTO (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade) VALUES
('2025-06-05 08:00:00',  35.0, 1, 6,  11, 1),
('2025-06-10 10:30:00',  50.0, 2, 6,  11, 2),
('2025-06-12 14:00:00', 130.0, 3, 6,  11, 3),
('2025-06-15 09:15:00',  28.0, 1, 6,  11, 1),
('2025-06-18 11:00:00',  95.0, 2, 7,  11, 2),
('2025-06-20 16:30:00', 245.0, 3, 7,  11, 3),
('2025-07-05 08:45:00',  12.0, 4, 8,  12, 1),
('2025-08-10 13:00:00',  48.0, 5, 8,  12, 2),
('2025-09-15 09:30:00',  32.0, 4, 9,  13, 3),
('2025-10-20 15:00:00', 250.0, 5, 10, 14, 1);

-- PROCEDIMENTOS REALIZADOS (10, um por atendimento)
INSERT INTO PROCEDIMENTO_REALIZADO (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, faturado) VALUES
(1,  5, 1,  12, 'Exame de rotina',              TRUE),
(2,  2, 1,  52, 'Suspeita de tumor',             FALSE),
(3,  3, 1, 128, 'Remocao de vesicula biliar',    FALSE),
(4,  1, 1,  35, 'Investigacao gastrica',          TRUE),
(5,  4, 1,  98, 'Avaliacao coronariana',          FALSE),
(6,  6, 1, 242, 'Insuficiencia renal cronica',    FALSE),
(7,  5, 2,  18, 'Coleta pre-cirurgica',           TRUE),
(8,  2, 1,  47, 'Controle pos-tratamento',        TRUE),
(9,  1, 1,  30, 'Rastreamento de rotina',         FALSE),
(10, 6, 1, 255, 'Sessao semanal de hemodialise',  FALSE);

-- ESCALAS DE PLANTAO (junho/2026)
INSERT INTO ESCALA_PLANTAO (id_residente, id_unidade, data_hora_inicio, data_hora_fim) VALUES
(6,  1, '2026-06-02 07:00:00', '2026-06-02 19:00:00'),
(7,  2, '2026-06-03 07:00:00', '2026-06-03 19:00:00'),
(8,  3, '2026-06-04 19:00:00', '2026-06-05 07:00:00'),
(9,  1, '2026-06-09 07:00:00', '2026-06-09 19:00:00'),
(10, 2, '2026-06-10 07:00:00', '2026-06-10 19:00:00'),
(6,  3, '2026-06-16 19:00:00', '2026-06-17 07:00:00'),
(7,  1, '2026-06-23 07:00:00', '2026-06-23 19:00:00'),
(8,  2, '2026-06-24 19:00:00', '2026-06-25 07:00:00');

COMMIT;
