import sys
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
import db
import crud
import queries


def cabecalho(titulo: str) -> None:
    print("\n" + "=" * 70)
    print(f" {titulo.upper()} ")
    print("=" * 70)


def obter_opcao(prompt: str, opcoes: list[str]) -> str:
    while True:
        opcao = input(prompt).strip()
        if opcao in opcoes:
            return opcao
        print(f"Opção inválida! Escolha entre: {', '.join(opcoes)}")


def obter_int(prompt: str, permitir_vazio=False) -> int | None:
    while True:
        valor = input(prompt).strip()
        if not valor and permitir_vazio:
            return None
        try:
            return int(valor)
        except ValueError:
            print("Entrada inválida! Digite um número inteiro.")


def obter_texto(prompt: str, permitir_vazio=False) -> str | None:
    while True:
        valor = input(prompt).strip()
        if not valor:
            if permitir_vazio:
                return None
            print("Entrada inválida! O campo não pode ficar vazio.")
            continue
        return valor


def obter_sim_nao(prompt: str) -> int:
    while True:
        valor = input(prompt).strip().lower()
        if valor in ("s", "sim", "1"):
            return 1
        if valor in ("n", "nao", "não", "0"):
            return 0
        print("Entrada inválida! Digite S para Sim ou N para Não.")


def obter_sim_nao_opcional(prompt: str) -> int | None:
    while True:
        valor = input(prompt).strip().lower()
        if not valor:
            return None
        if valor in ("s", "sim", "1"):
            return 1
        if valor in ("n", "nao", "não", "0"):
            return 0
        print("Entrada inválida! Digite S, N ou pressione Enter para manter o atual.")


def gerenciar_pacientes(conn) -> None:
    while True:
        cabecalho("Menu de Pacientes")
        print("1. Cadastrar Novo Paciente")
        print("2. Listar Todos os Pacientes")
        print("3. Atualizar Dados de um Paciente")
        print("4. Remover Paciente")
        print("0. Voltar ao Menu Principal")
        
        opcao = obter_opcao("\nEscolha uma opção: ", ["1", "2", "3", "4", "0"])
        
        if opcao == "0":
            break
            
        elif opcao == "1":
            cabecalho("Cadastrar Novo Paciente")
            nome = obter_texto("Nome: ")
            cpf = obter_texto("CPF: ")
            data_nascimento = obter_texto("Data de Nascimento (AAAA-MM-DD): ")
            is_flamengo = obter_sim_nao("É Flamenguista? (S/N): ")
            telefone = obter_texto("Telefone (opcional, Enter para pular): ", permitir_vazio=True)
            num_convenio = obter_texto("Número do Convênio (opcional): ", permitir_vazio=True)
            alergias = obter_texto("Alergias (opcional): ", permitir_vazio=True)
            grupo_sanguineo = obter_texto("Grupo Sanguíneo (A+, O-, etc., opcional): ", permitir_vazio=True)
            
            try:
                id_gerado = crud.inserir_paciente(
                    conn, nome, cpf, data_nascimento, is_flamengo, telefone,
                    num_convenio, alergias, grupo_sanguineo
                )
                print(f"\n[SUCESSO] Paciente cadastrado com ID: {id_gerado}")
            except UniqueViolation:
                conn.rollback()
                print("\n[ERRO] Já existe uma pessoa cadastrada com este CPF.")
            except Exception as e:
                conn.rollback()
                print(f"\n[ERRO] Não foi possível cadastrar o paciente: {e}")
                
        elif opcao == "2":
            cabecalho("Lista de Pacientes")
            pacientes = crud.listar_pacientes(conn)
            if not pacientes:
                print("Nenhum paciente cadastrado.")
            else:
                for p in pacientes:
                    flamengo_str = "Sim" if p["is_flamengo"] == 1 else "Não"
                    print(
                        f"ID: {p['id_pessoa']} | Nome: {p['nome']} | CPF: {p['cpf']} | "
                        f"Nasc: {p['data_nascimento']} | Flamengo: {flamengo_str} | "
                        f"Tel: {p['telefone'] or 'N/A'} | Convênio: {p['num_convenio'] or 'N/A'} | "
                        f"Alergias: {p['alergias'] or 'Nenhum'} | Sangue: {p['grupo_sanguineo'] or 'N/A'}"
                    )
                    
        elif opcao == "3":
            cabecalho("Atualizar Paciente")
            id_paciente = obter_int("Digite o ID do paciente que deseja atualizar: ")
            print("Deixe o campo vazio (pressione Enter) caso não deseje alterar o atributo.")
            nome = obter_texto("Novo Nome: ", permitir_vazio=True)
            cpf = obter_texto("Novo CPF: ", permitir_vazio=True)
            data_nascimento = obter_texto("Nova Data de Nascimento (AAAA-MM-DD): ", permitir_vazio=True)
            is_flamengo = obter_sim_nao_opcional("Novo status do Flamengo (S/N): ")
            telefone = obter_texto("Novo Telefone: ", permitir_vazio=True)
            num_convenio = obter_texto("Novo Convênio: ", permitir_vazio=True)
            alergias = obter_texto("Novas Alergias: ", permitir_vazio=True)
            grupo_sanguineo = obter_texto("Novo Grupo Sanguíneo: ", permitir_vazio=True)
            
            try:
                crud.atualizar_paciente(
                    conn, id_paciente, nome, cpf, data_nascimento, is_flamengo, telefone,
                    num_convenio, alergias, grupo_sanguineo
                )
                print("\n[SUCESSO] Paciente atualizado com sucesso.")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except Exception as e:
                conn.rollback()
                print(f"\n[ERRO] Não foi possível atualizar o paciente: {e}")
                
        elif opcao == "4":
            cabecalho("Remover Paciente")
            id_paciente = obter_int("Digite o ID do paciente que deseja remover: ")
            confirmar = obter_sim_nao(f"Tem certeza que deseja remover o paciente ID {id_paciente}? (S/N): ")
            if confirmar:
                try:
                    removido = crud.remover_pessoa(conn, id_paciente)
                    if removido:
                        print("\n[SUCESSO] Paciente removido com sucesso.")
                    else:
                        print(f"\n[ERRO] Paciente com ID {id_paciente} não foi encontrado.")
                except ForeignKeyViolation:
                    conn.rollback()
                    print("\n[AVISO] Este paciente possui atendimentos registrados e não pode ser removido.")
                except Exception as e:
                    conn.rollback()
                    print(f"\n[ERRO] Não foi possível remover: {e}")


def gerenciar_profissionais(conn) -> None:
    while True:
        cabecalho("Menu de Profissionais")
        print("1. Cadastrar Novo Profissional")
        print("2. Listar Todos os Profissionais")
        print("3. Atualizar Dados de um Profissional")
        print("4. Remover Profissional")
        print("0. Voltar ao Menu Principal")
        
        opcao = obter_opcao("\nEscolha uma opção: ", ["1", "2", "3", "4", "0"])
        
        if opcao == "0":
            break
            
        elif opcao == "1":
            cabecalho("Cadastrar Novo Profissional")
            nome = obter_texto("Nome: ")
            cpf = obter_texto("CPF: ")
            data_nascimento = obter_texto("Data de Nascimento (AAAA-MM-DD): ")
            is_flamengo = obter_sim_nao("É Flamenguista? (S/N): ")
            telefone = obter_texto("Telefone (opcional): ", permitir_vazio=True)
            crm = obter_texto("CRM: ")
            data_admissao = obter_texto("Data de Admissão (AAAA-MM-DD): ")
            especialidade = obter_texto("Especialidade: ")
            
            tipo = obter_opcao("Tipo de profissional (P para Preceptor, R para Residente): ", ["p", "r", "P", "R"]).lower()
            
            if tipo == "p":
                tipo_str = "preceptor"
                info_tipo = obter_texto("Titulação (especialista, mestre, doutor, livre-docente): ")
            else:
                tipo_str = "residente"
                info_tipo = obter_texto("Ano de Residência (R1, R2, R3): ")
                
            try:
                id_gerado = crud.inserir_profissional(
                    conn, nome, cpf, data_nascimento, is_flamengo, telefone,
                    crm, data_admissao, especialidade, tipo_str, info_tipo
                )
                print(f"\n[SUCESSO] Profissional cadastrado com ID: {id_gerado}")
            except UniqueViolation:
                conn.rollback()
                print("\n[ERRO] CPF ou CRM duplicado no sistema.")
            except Exception as e:
                conn.rollback()
                print(f"\n[ERRO] Não foi possível cadastrar o profissional: {e}")
                
        elif opcao == "2":
            cabecalho("Lista de Profissionais")
            profissionais = crud.listar_profissionais(conn)
            if not profissionais:
                print("Nenhum profissional cadastrado.")
            else:
                for p in profissionais:
                    flamengo_str = "Sim" if p["is_flamengo"] == 1 else "Não"
                    print(
                        f"ID: {p['id_pessoa']} | Nome: {p['nome']} | CPF: {p['cpf']} | "
                        f"CRM: {p['crm']} | Tipo: {p['tipo']} ({p['detalhe']}) | "
                        f"Admissão: {p['data_admissao']} | Especialidade: {p['especialidade']} | "
                        f"Flamengo: {flamengo_str} | Tel: {p['telefone'] or 'N/A'}"
                    )
                    
        elif opcao == "3":
            cabecalho("Atualizar Profissional")
            id_prof = obter_int("Digite o ID do profissional que deseja atualizar: ")
            print("Deixe o campo vazio (pressione Enter) caso não deseje alterar o atributo.")
            nome = obter_texto("Novo Nome: ", permitir_vazio=True)
            cpf = obter_texto("Novo CPF: ", permitir_vazio=True)
            data_nascimento = obter_texto("Nova Data de Nascimento (AAAA-MM-DD): ", permitir_vazio=True)
            is_flamengo = obter_sim_nao_opcional("Novo status do Flamengo (S/N): ")
            telefone = obter_texto("Novo Telefone: ", permitir_vazio=True)
            crm = obter_texto("Novo CRM: ", permitir_vazio=True)
            data_admissao = obter_texto("Nova Data de Admissão (AAAA-MM-DD): ", permitir_vazio=True)
            especialidade = obter_texto("Nova Especialidade: ", permitir_vazio=True)
            info_tipo = obter_texto("Novo Detalhe (Nova Titulação ou Novo Ano de Residência): ", permitir_vazio=True)
            
            try:
                crud.atualizar_profissional(
                    conn, id_prof, nome, cpf, data_nascimento, is_flamengo, telefone,
                    crm, data_admissao, especialidade, info_tipo
                )
                print("\n[SUCESSO] Profissional atualizado com sucesso.")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except UniqueViolation:
                conn.rollback()
                print("\n[ERRO] CPF ou CRM duplicado no sistema.")
            except Exception as e:
                conn.rollback()
                print(f"\n[ERRO] Não foi possível atualizar o profissional: {e}")
                
        elif opcao == "4":
            cabecalho("Remover Profissional")
            id_prof = obter_int("Digite o ID do profissional que deseja remover: ")
            confirmar = obter_sim_nao(f"Tem certeza que deseja remover o profissional ID {id_prof}? (S/N): ")
            if confirmar:
                try:
                    removido = crud.remover_pessoa(conn, id_prof)
                    if removido:
                        print("\n[SUCESSO] Profissional removido com sucesso.")
                    else:
                        print(f"\n[ERRO] Profissional com ID {id_prof} não encontrado.")
                except ForeignKeyViolation:
                    conn.rollback()
                    print("\n[AVISO] Este profissional possui atendimentos/escalas vinculados e não pode ser removido.")
                except Exception as e:
                    conn.rollback()
                    print(f"\n[ERRO] Não foi possível remover: {e}")


def gerenciar_atendimentos(conn) -> None:
    while True:
        cabecalho("Menu de Atendimentos")
        print("1. Registrar Novo Atendimento")
        print("2. Listar Atendimentos de um Paciente")
        print("0. Voltar ao Menu Principal")
        
        opcao = obter_opcao("\nEscolha uma opção: ", ["1", "2", "0"])
        
        if opcao == "0":
            break
            
        elif opcao == "1":
            cabecalho("Registrar Novo Atendimento")
            data_hora = obter_texto("Data e Hora (AAAA-MM-DD HH:MM): ")
            duracao = obter_int("Duração (em minutos): ")
            id_paciente = obter_int("ID do Paciente: ")
            id_residente = obter_int("ID do Residente: ")
            id_preceptor = obter_int("ID do Preceptor: ")
            
            try:
                id_gerado = crud.inserir_atendimento(conn, data_hora, duracao, id_paciente, id_residente, id_preceptor)
                print(f"\n[SUCESSO] Atendimento registrado com ID: {id_gerado}")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except Exception as e:
                conn.rollback()
                print(f"\n[ERRO] Falha ao registrar atendimento: {e}")
                
        elif opcao == "2":
            cabecalho("Listar Atendimentos por Paciente")
            id_paciente = obter_int("Digite o ID do Paciente: ")
            atendimentos = crud.listar_atendimentos_por_paciente(conn, id_paciente)
            
            if not atendimentos:
                print(f"Nenhum atendimento encontrado para o paciente ID {id_paciente}.")
            else:
                for a in atendimentos:
                    print(
                        f"ID Atendimento: {a['id_atendimento']} | Data/Hora: {a['data_hora']} | "
                        f"Duração: {a['duracao_minutos']} min | "
                        f"Residente: {a['nome_residente']} | Preceptor: {a['nome_preceptor']}"
                    )


def visualizar_relatorios(conn) -> None:
    while True:
        cabecalho("Relatórios & Queries Analíticas")
        print("1. Ranking de Residentes por Atendimentos")
        print("2. Preceptores com mais atendimentos no mês")
        print("3. Plantões escalados por residente, por unidade")
        print("4. Pacientes sem nenhum procedimento de risco ALTO")
        print("5. Duração média de atendimentos por residente")
        print("0. Voltar ao Menu Principal")
        
        opcao = obter_opcao("\nEscolha uma opção: ", ["1", "2", "3", "4", "5", "0"])
        
        if opcao == "0":
            break
            
        elif opcao == "1":
            cabecalho("Ranking de Residentes por Número de Atendimentos")
            res = queries.ranking_residentes_por_atendimentos(conn)
            for r in res:
                print(f"Residente: {r['nome_residente']} | Total Atendimentos: {r['total_atendimentos']}")
                
        elif opcao == "2":
            cabecalho("Preceptores com Atendimentos em Mês Específico")
            mes = obter_texto("Digite o mês/ano (AAAA-MM): ")
            minimo = obter_int("Mínimo de atendimentos (Enter para 1): ", permitir_vazio=True) or 1
            res = queries.preceptores_com_mais_de_n_atendimentos_no_mes(conn, mes, minimo)
            if not res:
                print("Nenhum preceptor atendeu a esses critérios no período.")
            else:
                for r in res:
                    print(f"Preceptor: {r['nome_preceptor']} | Atendimentos: {r['total_atendimentos']}")
                    
        elif opcao == "3":
            cabecalho("Plantões Escalados por Residente / Unidade")
            res = queries.plantoes_escalados_por_residente_por_unidade(conn)
            for r in res:
                print(f"Unidade: {r['nome_unidade']} | Residente: {r['nome_residente']} | Total Plantões: {r['total_plantoes']}")
                
        elif opcao == "4":
            cabecalho("Pacientes Sem Nenhum Procedimento de Risco ALTO")
            res = queries.pacientes_sem_procedimento_alto_risco(conn)
            for r in res:
                print(f"Paciente: {r['nome_paciente']} | Convênio: {r['num_convenio'] or 'N/A'}")
                
        elif opcao == "5":
            cabecalho("Duração Média de Atendimento por Residente")
            res = crud.tempo_medio_por_residente(conn)
            for r in res:
                print(f"Residente: {r['nome_residente']} | Média: {float(r['media_duracao_minutos']):.1f} min | Total Atendimentos: {r['total_atendimentos']}")


def main() -> None:
    try:
        conn = db.get_connection()
    except psycopg2.OperationalError as e:
        print("[ERRO CRÍTICO] Falha ao conectar ao PostgreSQL.")
        print("Por favor, verifique se o servidor está ativo e se os dados no arquivo .env estão corretos.")
        print(f"Detalhes: {e}")
        sys.exit(1)
        
    while True:
        cabecalho("Sistema de Gestão Hospitalar - CRUD & Analítico")
        print("1. Gerenciar Pacientes")
        print("2. Gerenciar Profissionais")
        print("3. Gerenciar Atendimentos")
        print("4. Relatórios & Queries Analíticas")
        print("5. Resetar e Repovoar Banco de Dados (Seed)")
        print("0. Sair do Sistema")
        
        opcao = obter_opcao("\nEscolha uma opção: ", ["1", "2", "3", "4", "5", "0"])
        
        if opcao == "0":
            print("\nEncerrando sistema. Até logo!")
            conn.close()
            break
            
        elif opcao == "1":
            gerenciar_pacientes(conn)
            
        elif opcao == "2":
            gerenciar_profissionais(conn)
            
        elif opcao == "3":
            gerenciar_atendimentos(conn)
            
        elif opcao == "4":
            visualizar_relatorios(conn)
            
        elif opcao == "5":
            confirmar = obter_sim_nao("\nTem certeza que deseja resetar TODAS as tabelas e dados? (S/N): ")
            if confirmar:
                try:
                    conn.close()
                    conn = db.init_db(reset=True, seed=True)
                    print("\n[SUCESSO] Banco de dados resetado e repovoado com sucesso.")
                except Exception as e:
                    print(f"\n[ERRO] Não foi possível resetar o banco de dados: {e}")
                    # Restabelecer a conexão
                    conn = db.get_connection()


if __name__ == "__main__":
    main()
