INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
('Ana Souza', '111.111.111-01', '1990-02-10', 1, '21988880001'),
('Bruno Lima', '111.111.111-02', '1985-06-21', 0, '21988880002'),
('Carla Mendes', '111.111.111-03', '2001-11-03', 1, '21988880003'),
('Diego Alves', '111.111.111-04', '1975-01-30', 0, '21988880004'),
('Elisa Farias', '111.111.111-05', '1999-09-15', 0, '21988880005');

INSERT INTO PACIENTE (id_pessoa, num_convenio, alergias, grupo_sanguineo) VALUES
(1, 'CV-1001', 'Dipirona', 'O+'),
(2, 'CV-1002', 'Nenhuma', 'A+'),
(3, 'CV-1003', 'Penicilina', 'B-'),
(4, 'CV-1004', 'Nenhuma', 'AB+'),
(5, 'CV-1005', 'Latex', 'O-');

INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone) VALUES
('Dr. Marcos Rezende', '222.222.222-01', '1970-03-12', 1, '21977770001'),
('Dra. Paula Nogueira', '222.222.222-02', '1972-07-19', 0, '21977770002'),
('Dr. Ricardo Teixeira', '222.222.222-03', '1968-05-25', 1, '21977770003'),
('Dra. Sandra Vieira', '222.222.222-04', '1980-12-01', 0, '21977770004'),
('Dr. Otavio Cunha', '222.222.222-05', '1965-04-08', 0, '21977770005');

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
('Gustavo Pires', '333.333.333-01', '1996-01-11', 1, '21966660001'),
('Helena Duarte', '333.333.333-02', '1997-08-22', 0, '21966660002'),
('Igor Barros', '333.333.333-03', '1995-04-05', 1, '21966660003'),
('Julia Ramos', '333.333.333-04', '1998-10-30', 0, '21966660004'),
('Kaique Moraes', '333.333.333-05', '1994-12-19', 1, '21966660005');

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

INSERT INTO ATENDIMENTO (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor) VALUES
('2025-05-02 08:00', 45, 1, 11, 6),
('2025-05-03 09:30', 30, 2, 12, 7),
('2025-05-04 14:00', 60, 3, 13, 8),
('2025-05-05 10:15', 25, 4, 14, 9),
('2025-05-06 16:45', 50, 5, 15, 10),
('2025-05-07 11:00', 35, 1, 12, 7),
('2025-05-08 13:20', 40, 2, 13, 8),
('2025-05-09 07:50', 20, 3, 14, 9),
('2025-05-10 18:10', 55, 4, 15, 10),
('2025-05-11 09:00', 30, 5, 11, 6);

INSERT INTO PROCEDIMENTO_REALIZADO
    (id_atendimento, id_procedimento, quantidade, tempo_real_minutos, observacao, faturado) VALUES
(1, 1, 1, 22, 'Sem intercorrencias', 0),
(2, 2, 1, 8, 'Coleta rapida', 1),
(3, 4, 1, 18, 'Paciente estavel apos procedimento', 1),
(4, 3, 2, 6, 'Duas doses aplicadas', 0),
(5, 5, 1, 35, 'Necessario segundo profissional', 1),
(6, 6, 1, 28, 'Curativo trocado', 0),
(7, 7, 1, 45, 'Fratura reduzida com sucesso', 1),
(8, 9, 1, 17, 'Sem complicacoes', 0),
(9, 10, 1, 22, 'Parada revertida', 1),
(10, 8, 1, 25, 'Procedimento eletivo', 0);

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
