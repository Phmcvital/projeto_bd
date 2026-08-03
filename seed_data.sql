INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
('Ana Souza', '111.111.111-01', '1990-02-10', TRUE, '21988880001'),
('Bruno Lima', '111.111.111-02', '1985-06-21', FALSE, '21988880002'),
('Carla Mendes', '111.111.111-03', '2001-11-03', TRUE, '21988880003'),
('Diego Alves', '111.111.111-04', '1975-01-30', FALSE, '21988880004'),
('Elisa Farias', '111.111.111-05', '1999-09-15', FALSE, '21988880005');

INSERT INTO PACIENTE (id_pessoa, num_convenio, alergias, grupo_sanguineo) VALUES
(1, 'CV-1001', 'Dipirona', 'O+'),
(2, 'CV-1002', 'Nenhuma', 'A+'),
(3, 'CV-1003', 'Penicilina', 'B-'),
(4, 'CV-1004', 'Nenhuma', 'AB+'),
(5, 'CV-1005', 'Latex', 'O-');

INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
('Dr. Marcos Rezende', '222.222.222-01', '1970-03-12', TRUE, '21977770001'),
('Dra. Paula Nogueira', '222.222.222-02', '1972-07-19', FALSE, '21977770002'),
('Dr. Ricardo Teixeira', '222.222.222-03', '1968-05-25', TRUE, '21977770003'),
('Dra. Sandra Vieira', '222.222.222-04', '1980-12-01', FALSE, '21977770004'),
('Dr. Otavio Cunha', '222.222.222-05', '1965-04-08', FALSE, '21977770005');

INSERT INTO PROFISSIONAL (id_pessoa, crm, data_admissao, especialidade) VALUES
(6, 'CRM-11111', '2005-01-10', 'Clinica Medica'),
(7, 'CRM-22222', '2007-03-15', 'Pediatria'),
(8, 'CRM-33333', '2000-06-20', 'Cirurgia Geral'),
(9, 'CRM-44444', '2010-09-01', 'Ortopedia'),
(10, 'CRM-55555', '1998-02-14', 'Cardiologia');

INSERT INTO PRECEPTOR (id_profissional, titulacao) VALUES
(6, 'doutor'),
(7, 'mestre'),
(8, 'livre-docente'),
(9, 'especialista'),
(10, 'doutor');

INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
('Gustavo Pires', '333.333.333-01', '1996-01-11', TRUE, '21966660001'),
('Helena Duarte', '333.333.333-02', '1997-08-22', FALSE, '21966660002'),
('Igor Barros', '333.333.333-03', '1995-04-05', TRUE, '21966660003'),
('Julia Ramos', '333.333.333-04', '1998-10-30', FALSE, '21966660004'),
('Kaique Moraes', '333.333.333-05', '1994-12-19', TRUE, '21966660005');

INSERT INTO PROFISSIONAL (id_pessoa, crm, data_admissao, especialidade) VALUES
(11, 'CRM-66666', '2023-02-01', 'Clinica Medica'),
(12, 'CRM-77777', '2022-02-01', 'Pediatria'),
(13, 'CRM-88888', '2021-02-01', 'Cirurgia Geral'),
(14, 'CRM-99999', '2023-02-01', 'Ortopedia'),
(15, 'CRM-10101', '2022-02-01', 'Cardiologia');

INSERT INTO RESIDENTE (id_profissional, ano_residencia) VALUES
(11, 'R1'),
(12, 'R2'),
(13, 'R3'),
(14, 'R1'),
(15, 'R2');

INSERT INTO UNIDADE (nome, tipo, capacidade_leitos) VALUES
('Enfermaria Ala Norte', 'Enfermaria', 40),
('UTI Adulto', 'UTI', 12),
('Pronto-Socorro Central','Pronto-Socorro', 20);

INSERT INTO PROCEDIMENTO (codigo, nome, tempo_medio_minutos, nivel_risco) VALUES
('P001', 'Sutura simples', 20, 'BAIXO'),
('P002', 'Coleta de sangue', 10, 'BAIXO'),
('P003', 'Aplicacao de medicacao', 5, 'BAIXO'),
('P004', 'Intubacao orotraqueal', 15, 'ALTO'),
('P005', 'Dreno toracico', 30, 'ALTO'),
('P006', 'Curativo complexo', 25, 'MEDIO'),
('P007', 'Reducao de fratura', 40, 'ALTO'),
('P008', 'Punção lombar', 20, 'MEDIO'),
('P009', 'Cateterismo vesical', 15, 'BAIXO'),
('P010', 'Ressuscitacao cardiopulmonar', 20, 'ALTO');

INSERT INTO ATENDIMENTO
    (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor, id_unidade)
VALUES
('2025-05-02 08:00', 45, 1, 11, 6, 1),
('2025-05-03 09:30', 30, 2, 12, 7, 1),
('2025-05-04 14:00', 60, 3, 13, 8, 2),
('2025-05-05 10:15', 25, 4, 14, 9, 3),
('2025-05-06 16:45', 50, 5, 15, 10, 2),
('2025-05-07 11:00', 35, 1, 12, 7, 1),
('2025-05-08 13:20', 40, 2, 13, 8, 2),
('2025-05-09 07:50', 20, 3, 14, 9, 3),
('2025-05-10 18:10', 55, 4, 15, 10, 2),
('2025-05-11 09:00', 30, 5, 11, 6, 1);

INSERT INTO PROCEDIMENTO_REALIZADO
    (id_atendimento, id_procedimento, quantidade, data_hora_inicio,
     tempo_real_minutos, observacao, faturado)
VALUES
(1, 1, 1, '2025-05-02 08:08', 22, 'Sem intercorrencias', FALSE),
(2, 2, 1, '2025-05-03 09:42', 8, 'Coleta rapida', TRUE),
(3, 4, 1, '2025-05-04 14:10', 18, 'Paciente estavel apos procedimento', TRUE),
(4, 3, 2, '2025-05-05 10:20', 6, 'Duas doses aplicadas', FALSE),
(5, 5, 1, '2025-05-06 17:00', 35, 'Necessario segundo profissional', TRUE),
(6, 6, 1, '2025-05-07 11:09', 28, 'Curativo trocado', FALSE),
(7, 7, 1, '2025-05-08 13:35', 45, 'Fratura reduzida com sucesso', TRUE),
(8, 9, 1, '2025-05-09 07:57', 17, 'Sem complicacoes', FALSE),
(9, 10, 1, '2025-05-10 18:20', 22, 'Parada revertida', TRUE),
(10, 8, 1, '2025-05-11 09:11', 25, 'Procedimento eletivo', FALSE);

INSERT INTO INTERNACAO
    (id_paciente, id_unidade, data_hora_entrada, data_hora_saida)
VALUES
(1, 1, '2025-05-02 09:00', '2025-05-05 14:00'),
(3, 2, '2025-05-04 15:30', NULL),
(5, 1, '2025-05-11 10:00', NULL);

INSERT INTO ESCALA (id_unidade, dia_semana, turno, id_residente, id_preceptor) VALUES
(1, 'segunda', 'manha', 11, 6),
(1, 'terca', 'tarde', 12, 7),
(2, 'quarta', 'noite', 13, 8),
(2, 'quinta', 'manha', 14, 9),
(3, 'sexta', 'tarde', 15, 10),
(3, 'sabado', 'noite', 11, 6),
(1, 'domingo', 'manha', 12, 7),
(2, 'segunda', 'tarde', 13, 8),
(3, 'terca', 'noite', 14, 9),
(1, 'quarta', 'manha', 15, 10);
