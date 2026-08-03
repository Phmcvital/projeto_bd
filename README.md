# Sistema de Gestão Hospitalar — Etapa 2

Projeto da disciplina de Banco de Dados. A aplicação de terminal da Etapa 1 foi
mantida e migrada para SQLAlchemy. A Etapa 2 acrescenta procedures, triggers,
views, consultas avançadas com ORM e uma demonstração de concorrência.

## Tecnologias

- PostgreSQL;
- Python 3.10 ou superior;
- SQLAlchemy;
- psycopg 3.

## Configuração inicial

1. Crie um banco PostgreSQL chamado `hospital`:

```sql
CREATE DATABASE hospital;
```

2. Crie o arquivo local de configuração:

```powershell
Copy-Item .env.example .env
```

3. Abra `.env` e informe usuário e senha corretos do PostgreSQL.

4. Instale somente as dependências do projeto:

```powershell
python -m pip install -r requirements.txt
```

5. Monte as tabelas, objetos da Etapa 2 e dados de demonstração:

```powershell
python db.py
```

Esse último comando recria o schema `public` do banco configurado no `.env`.
Ele deve ser usado no banco acadêmico `hospital`, não em um banco com dados
importantes.

6. Execute a interface:

```powershell
python main.py
```

## O que foi implementado

### Stored procedures

- `sp_registrar_atendimento_completo`: recebe os dados do atendimento e um
  array JSON de procedimentos. Se qualquer item for inválido, o PostgreSQL
  desfaz toda a chamada;
- `sp_calcular_tempo_medio_espera`: calcula a espera entre a chegada e o início
  do primeiro procedimento de cada atendimento. O resultado fica na tabela
  temporária `resultado_tempo_medio_espera` durante a sessão;
- `sp_reajustar_escala`: altera as escalas de um residente de um dia/turno para
  outro e cancela a operação quando há conflito.

### Triggers

- `trg_check_sobreposicao_escala`: bloqueia um residente no mesmo dia e turno
  em unidades diferentes;
- `trg_audita_atendimento`: registra INSERT, UPDATE e DELETE, usuário, horário
  e estados antigo/novo em JSONB;
- `trg_atualiza_media_procedimentos`: recalcula a média real do procedimento
  após cada realização inserida.

### Views

- `vw_pacientes_internados`;
- `vw_residentes_sem_supervisor`;
- `vw_estatisticas_atendimentos_mensal`.

### ORM

O arquivo `models.py` contém uma classe para cada entidade. `crud.py` substitui
as operações SQL da Etapa 1 por sessões e objetos SQLAlchemy. `queries.py`
contém tanto os relatórios anteriores quanto as três consultas avançadas:

- preceptores que supervisionaram atendimentos de pacientes flamenguistas;
- último atendimento de cada paciente, com seus relacionamentos;
- percentual de procedimentos de alto risco por residente.

A função `demonstrar_lazy_e_eager_loading` mostra os dois carregamentos. O lazy
loading consulta a relação ao acessá-la; o eager loading usa `selectinload` ou
`joinedload` para planejar a carga junto da consulta.

## Concorrência

Execute:

```powershell
python concorrencia.py
```

Duas threads, cada uma com sua própria sessão e transação, tentam escalar o
mesmo residente no mesmo horário. A primeira obtém um bloqueio pessimista com
`SELECT ... FOR UPDATE`. A segunda aguarda; quando prossegue, percebe que a
escala já existe e faz rollback. O resultado aparece no terminal e no arquivo
`concorrencia.log`.

## Testes manuais

O arquivo `testes_etapa2.sql` contém chamadas e consultas prontas para executar
no Query Tool do pgAdmin. Alguns testes usam `BEGIN` e `ROLLBACK`, evitando
alterar os dados de demonstração.

Para executar a bateria automatizada completa:

```powershell
python verificar_etapa2.py
```

Ela verifica os objetos PostgreSQL, procedures, transações, auditoria, views,
consultas ORM, lazy/eager loading e concorrência. Os dados temporários usados
nos testes são revertidos ou removidos ao final.

Ordem recomendada para uma demonstração:

1. executar `python db.py`;
2. executar `python main.py` e abrir as funcionalidades da Etapa 2;
3. testar as três consultas ORM no menu de relatórios;
4. executar `python concorrencia.py`;
5. conferir o arquivo `concorrencia.log`.

## Arquivos principais

- `schema.sql`: tabelas e índices;
- `etapa2.sql`: procedures, triggers e views;
- `seed_data.sql`: dados de teste;
- `models.py`: entidades SQLAlchemy;
- `crud.py`: CRUD por ORM;
- `queries.py`: consultas por ORM;
- `servicos_etapa2.py`: chamadas das procedures e views;
- `concorrencia.py`: cenário de duas transações;
- `verificar_etapa2.py`: bateria automatizada da entrega;
- `RELATORIO_ETAPA2.md`: decisões de implementação;
