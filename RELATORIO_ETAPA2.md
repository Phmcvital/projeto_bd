# Relatório de implementação — Etapa 2

## 1. Evolução do banco de dados

A Etapa 1 já possuía as entidades centrais do hospital e uma aplicação de
terminal construída com Python. Para atender à Etapa 2 foi necessário evoluir
o esquema sem alterar a ideia original do projeto. O banco adotado continuou
sendo o PostgreSQL.

Alguns requisitos novos dependiam de dados que ainda não existiam. A tabela
ATENDIMENTO recebeu `id_unidade`, pois estatísticas e tempo de espera precisam
ser calculados por unidade. PROCEDIMENTO_REALIZADO recebeu
`data_hora_inicio`, possibilitando medir a diferença entre a chegada do
paciente e o primeiro procedimento. PROCEDIMENTO recebeu
`media_tempo_procedimento`, valor mantido automaticamente por trigger. Também
foram criadas INTERNACAO, necessária para identificar pacientes internados, e
AUDITORIA_ATENDIMENTO, necessária para preservar o histórico das alterações.

Os horários passaram a usar TIMESTAMP e os indicadores lógicos passaram a usar
BOOLEAN. Esses tipos representam melhor os valores do domínio e permitem que o
PostgreSQL realize cálculos e filtros diretamente, sem conversões de texto.

## 2. Procedures e transações

A procedure `sp_registrar_atendimento_completo` concentra uma operação de
negócio que envolve duas tabelas: primeiro insere ATENDIMENTO e depois percorre
uma lista JSON para inserir cada PROCEDIMENTO_REALIZADO. O JSON foi escolhido
porque permite enviar vários procedimentos em um único parâmetro e é suportado
nativamente pelo PostgreSQL. Não foi criada uma estrutura intermediária na
aplicação.

A chamada é atômica. O código não captura nem ignora erros de chave estrangeira,
chave primária ou CHECK. Portanto, se um procedimento for inválido, o erro sobe
para a transação e o PostgreSQL desfaz inclusive o atendimento que tinha sido
inserido antes. Essa regra evita atendimentos incompletos.

A `sp_calcular_tempo_medio_espera` encontra, com MIN, o primeiro horário de
procedimento de cada atendimento. Em seguida calcula a diferença em minutos e
a média por unidade. Como procedures do PostgreSQL não retornam uma tabela da
mesma forma que uma consulta SELECT, foi utilizada uma tabela temporária da
sessão. Depois do CALL, o resultado pode ser consultado de forma simples. Essa
solução mantém o objeto como procedure, conforme solicitado, e não grava um
relatório permanente que poderia ficar desatualizado.

A `sp_reajustar_escala` recebe o residente, dia e turno de origem e os novos
valores. Antes do UPDATE ela verifica a existência da escala e procura conflito
na mesma unidade. Caso encontre um conflito, lança uma exceção e nenhuma escala
é alterada. O trigger de sobreposição atua como uma segunda proteção para o
caso de unidades diferentes.

## 3. Triggers e views

Triggers foram escolhidos somente para regras que devem valer
independentemente de qual aplicação altere o banco. O
`trg_check_sobreposicao_escala` roda antes de INSERT ou UPDATE e impede que o
mesmo residente fique em unidades diferentes no mesmo dia e turno. A restrição
UNIQUE existente continua impedindo duplicidade dentro da mesma unidade.

O `trg_audita_atendimento` roda depois de INSERT, UPDATE e DELETE. O PostgreSQL
fornece os registros OLD e NEW, que são convertidos para JSONB. Assim, uma única
tabela de auditoria consegue guardar o estado completo antes e depois de cada
operação, junto do usuário e do horário do banco. A auditoria não possui chave
estrangeira para ATENDIMENTO porque seu histórico deve permanecer mesmo quando
o atendimento for excluído.

O `trg_atualiza_media_procedimentos` roda depois de inserir um procedimento
realizado. Ele recalcula com AVG a média de tempo real daquele procedimento e
atualiza apenas sua linha em PROCEDIMENTO. A trigger é apropriada porque a média
precisa permanecer correta mesmo se a inserção não vier da aplicação Python.

As três views deixam consultas recorrentes prontas para uso. A primeira mostra
a internação aberta mais recente de cada paciente. A segunda mostra escalas
cujos preceptores não têm titulação de doutor. A terceira agrupa atendimentos
por mês e unidade, trazendo quantidade, duração média e o procedimento mais
frequente. Views foram usadas porque não alteram dados e oferecem uma forma
simples de reutilizar consultas de relatório.

## 4. Escolha e uso da ORM

Foi escolhida SQLAlchemy por ser a opção recomendada para Python e por separar
o código orientado a objetos dos detalhes do driver PostgreSQL. Cada tabela foi
mapeada para uma classe em `models.py`, com chaves, restrições e relacionamentos.
As operações da Etapa 1 foram reimplementadas em `crud.py` usando objetos,
`select`, filtros, joins e agregações da ORM. Não há SQL cru nessas consultas.

Cada alteração chama `commit` quando termina. Se ocorre uma exceção, é feito
`rollback`. Esse padrão demonstra claramente o uso de sessões e transações sem
adicionar camadas de arquitetura que não seriam necessárias para o trabalho.
As procedures e views são chamadas em `servicos_etapa2.py`; nesse ponto textos
SQL curtos são necessários porque CALL e views são objetos próprios do banco,
e não substituem as consultas ORM exigidas.

Os relacionamentos usam lazy loading por padrão: por exemplo, os atendimentos
de um paciente são buscados quando o atributo é acessado. Nas telas que já
sabem que precisarão dos dados relacionados, são usados `joinedload` e
`selectinload`. A consulta do último atendimento carrega residente, preceptor e
procedimentos antecipadamente, evitando consultas repetidas durante a exibição.

As consultas avançadas também foram feitas pela DSL da ORM. Foram implementados
o DISTINCT de preceptores ligados a pacientes flamenguistas, a busca do último
atendimento de cada paciente e a agregação do percentual de procedimentos de
alto risco por residente.

## 5. Concorrência

O cenário de concorrência usa duas threads apenas para representar dois usuários
simultâneos. Cada thread cria sua própria Session, portanto possui uma transação
independente. Ambas tentam inserir a mesma escala. A primeira seleciona o
residente com `FOR UPDATE` e mantém o bloqueio por dois segundos. A segunda fica
aguardando a liberação desse registro. Depois do COMMIT da primeira, a segunda
consulta novamente o horário, encontra a escala e executa ROLLBACK.

Foi escolhido o lock pessimista porque o conflito é esperado na demonstração e
o PostgreSQL consegue serializar as decisões de forma direta. Além do bloqueio,
a restrição UNIQUE e o trigger continuam protegendo o banco. O programa grava
horário, início, obtenção do lock, commit ou rollback em `concorrencia.log`,
permitindo comprovar a ordem dos acontecimentos no vídeo e na correção.
