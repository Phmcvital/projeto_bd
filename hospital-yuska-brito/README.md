# Sistema de Gestão Hospitalar — Hospital Universitário Dra. Yuska Maritan Brito

Projeto de banco de dados para o gerenciamento de pacientes, profissionais,
atendimentos, procedimentos, unidades hospitalares e escalas de plantão.

O projeto foi desenvolvido em SQL puro para PostgreSQL e contempla modelagem,
criação do banco, massa de dados, operações de CRUD e consultas analíticas.

## Funcionalidades

- Cadastro de pessoas, pacientes, residentes e preceptores.
- Registro de unidades, atendimentos e procedimentos realizados.
- Controle de escalas semanais de plantão.
- Operações de inserção, consulta, atualização e remoção.
- Consultas analíticas sobre atendimentos, supervisões, plantões e riscos.

## Tecnologias

- PostgreSQL.
- SQL e PL/pgSQL.
- pgAdmin ou outro cliente compatível com PostgreSQL.

O projeto foi validado com PostgreSQL 17 e pgAdmin 4.

## Estrutura do projeto

```text
hospital-yuska-brito/
├── docs/
│   ├── dre.pdf
│   ├── der.txt
│   └── DBML_resumo.txt
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_insert_data.sql
│   ├── 03_crud.sql
│   └── 04_consultas_analiticas.sql
└── README.md
```

### Scripts SQL

| Arquivo | Finalidade |
|---|---|
| `01_create_tables.sql` | Criação das tabelas, chaves e restrições. |
| `02_insert_data.sql` | Inserção da massa de dados para testes. |
| `03_crud.sql` | Procedure e exemplos de operações CRUD e consultas básicas. |
| `04_consultas_analiticas.sql` | Consultas analíticas solicitadas na etapa 4. |

## Instalação e execução

### Pré-requisitos

- PostgreSQL instalado localmente ou disponível em um contêiner.
- Um cliente SQL, como `psql`, pgAdmin ou DBeaver.

### Opção 1 — Terminal com `psql`

Crie um banco de dados vazio:

```bash
createdb -U postgres hospital_yuska
```

Crie as tabelas e insira a massa de dados:

```bash
psql -U postgres -v ON_ERROR_STOP=1 -d hospital_yuska -f sql/01_create_tables.sql
psql -U postgres -v ON_ERROR_STOP=1 -d hospital_yuska -f sql/02_insert_data.sql
```

Execute as consultas analíticas sobre a massa de dados original:

```bash
psql -U postgres -v ON_ERROR_STOP=1 -d hospital_yuska -f sql/04_consultas_analiticas.sql
```

Para demonstrar as operações de CRUD:

```bash
psql -U postgres -v ON_ERROR_STOP=1 -d hospital_yuska -f sql/03_crud.sql
```

### Opção 2 — pgAdmin

1. Conecte-se a uma instância PostgreSQL.
2. Crie um banco vazio chamado `hospital_yuska`.
3. Abra o **Query Tool** conectado ao banco criado.
4. Abra e execute `sql/01_create_tables.sql`.
5. Abra e execute `sql/02_insert_data.sql`.
6. Abra `sql/04_consultas_analiticas.sql` e execute cada consulta
   separadamente para visualizar os resultados.
7. Execute as operações de `sql/03_crud.sql` separadamente quando desejar
   demonstrar o CRUD.

## Ordem de execução e cuidados

Os scripts `01_create_tables.sql` e `02_insert_data.sql` pressupõem um banco
vazio. Para repetir todo o processo, utilize um novo banco ou recrie o banco de
demonstração.

O arquivo `03_crud.sql` não contém apenas definições: seus exemplos inserem,
atualizam e removem dados. Por isso, sua execução modifica os resultados das
consultas analíticas posteriores. Para conferir os resultados originais da
massa de teste, execute os scripts na seguinte ordem:

```text
01_create_tables.sql
02_insert_data.sql
04_consultas_analiticas.sql
```

Execute `03_crud.sql` depois das consultas analíticas ou em outro banco de
demonstração. Os identificadores e as datas presentes nos exemplos podem ser
ajustados antes da execução.

## Consultas analíticas

O arquivo `04_consultas_analiticas.sql` implementa:

1. Ranking dos residentes por quantidade de atendimentos.
2. Preceptores com mais de cinco atendimentos supervisionados em um mês.
3. Quantidade de plantões por residente e unidade no mês corrente.
4. Pacientes que nunca realizaram procedimentos de risco `ALTO`.

A tabela `ESCALA` representa uma escala semanal recorrente. Por esse motivo, a
terceira consulta utiliza `GENERATE_SERIES` para projetar os dias da semana sobre
o mês corrente.

## Resultados esperados

Com um banco novo, após executar somente os scripts `01` e `02`:

- O ranking contém cinco residentes; Gabriel Barbosa possui quatro
  atendimentos.
- Arthur Antunes Coimbra supervisionou seis atendimentos em junho de 2025.
- A consulta de plantões varia entre quatro e cinco ocorrências por escala,
  conforme o calendário do mês corrente.
- Erick Pulgar, Gerson Santos de Oliveira e Leonardo Ortiz não possuem
  procedimentos de risco `ALTO`.

## Apresentação

Para uma demonstração reproduzível:

1. Mostre o diagrama e as relações principais disponíveis em `docs/`.
2. Apresente as restrições e chaves definidas em `01_create_tables.sql`.
3. Mostre a massa de testes de `02_insert_data.sql`.
4. Execute as operações de `03_crud.sql` individualmente em um banco de teste.
5. Execute as quatro consultas de `04_consultas_analiticas.sql` separadamente.

---

Desenvolvido para a disciplina de Banco de Dados.
