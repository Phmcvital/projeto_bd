# Roteiro do vídeo da Etapa 2 (até 8 minutos)

## 0:00–0:40 — Introdução

- Mostrar a branch `etapa2` e a estrutura dos arquivos.
- Explicar que a interface da Etapa 1 foi preservada e migrada para SQLAlchemy.

## 0:40–2:15 — Procedures

- Abrir `etapa2.sql` nos nomes das três procedures.
- Na interface, registrar um atendimento com dois procedimentos.
- Mostrar que atendimento e lista são enviados juntos em JSON.
- Explicar que um erro em qualquer procedimento causa rollback de toda a chamada.
- Executar o cálculo do tempo médio de espera e mostrar o resultado por unidade.
- Reajustar uma escala válida; em seguida comentar que conflitos geram exceção.

## 2:15–3:35 — Triggers

- Mostrar os três `CREATE TRIGGER` no arquivo SQL.
- Abrir a auditoria na interface e apontar operação, usuário, horário e JSON.
- Consultar PROCEDIMENTO e mostrar `media_tempo_procedimento` preenchida.
- No Query Tool, usar o INSERT comentado de `testes_etapa2.sql` para demonstrar
  que a sobreposição de escala é recusada.
- Explicar a decisão: trigger protege a regra mesmo fora da aplicação; procedure
  representa uma operação de negócio chamada intencionalmente.

## 3:35–4:25 — Views

- Consultar no menu as três views.
- Mostrar pacientes atualmente internados.
- Mostrar escalas com preceptor sem titulação de doutor.
- Mostrar o resumo mensal por unidade.

## 4:25–5:55 — ORM

- Abrir rapidamente `models.py` e mostrar Pessoa, Paciente, Atendimento e seus
  `relationship`.
- Abrir `crud.py` e destacar `select`, `sessao.add`, `commit` e `rollback`.
- Executar no menu as três consultas avançadas da Etapa 2.
- Executar a opção lazy/eager loading e explicar:
  - lazy busca a relação quando ela é acessada;
  - eager usa `joinedload`/`selectinload` quando a relação já será necessária.

## 5:55–7:05 — Concorrência

- Executar `python concorrencia.py`.
- Apontar nos logs que T1 obtém o lock primeiro.
- Mostrar que T2 espera, encontra a escala confirmada e faz rollback.
- Mostrar o resultado final de exatamente uma escala.
- Abrir `concorrencia.log` para provar que os logs também ficaram gravados.

## 7:05–7:40 — Encerramento

- Mostrar `RELATORIO_ETAPA2.md`.
- Resumir as escolhas: SQLAlchemy, transações por Session e lock pessimista.
- Mostrar `git log --oneline --all --decorate` para diferenciar Etapa 1 e Etapa 2.
