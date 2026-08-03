import sys
from sqlalchemy.orm import Session
from sqlalchemy import text
import db
import orm_crud as crud
import orm_queries as queries


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
        print("Entrada inválida! Digite S, N ou pressione Enter para manter.")


def gerenciar_pacientes(session: Session) -> None:
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
            telefone = obter_texto("Telefone (opcional): ", permitir_vazio=True)
            num_convenio = obter_texto("Número do Convênio (opcional): ", permitir_vazio=True)
            alergias = obter_texto("Alergias (opcional): ", permitir_vazio=True)
            grupo_sanguineo = obter_texto("Grupo Sanguíneo (opcional): ", permitir_vazio=True)
            try:
                id_gerado = crud.inserir_paciente(
                    session, nome, cpf, data_nascimento, is_flamengo, telefone,
                    num_convenio, alergias, grupo_sanguineo,
                )
                print(f"\n[SUCESSO] Paciente cadastrado com ID: {id_gerado}")
            except Exception as e:
                session.rollback()
                print(f"\n[ERRO] Não foi possível cadastrar o paciente: {e}")

        elif opcao == "2":
            cabecalho("Lista de Pacientes")
            pacientes = crud.listar_pacientes(session)
            if not pacientes:
                print("Nenhum paciente cadastrado.")
            else:
                for p in pacientes:
                    flamengo_str = "Sim" if p.Pessoa.is_flamengo == 1 else "Não"
                    print(
                        f"ID: {p.Pessoa.id_pessoa} | Nome: {p.Pessoa.nome} | CPF: {p.Pessoa.cpf} | "
                        f"Nasc: {p.Pessoa.data_nascimento} | Flamengo: {flamengo_str} | "
                        f"Tel: {p.Pessoa.telefone or 'N/A'} | Convênio: {p.Paciente.num_convenio or 'N/A'} | "
                        f"Alergias: {p.Paciente.alergias or 'Nenhum'} | Sangue: {p.Paciente.grupo_sanguineo or 'N/A'}"
                    )

        elif opcao == "3":
            cabecalho("Atualizar Paciente")
            id_paciente = obter_int("Digite o ID do paciente: ")
            print("Deixe vazio para não alterar.")
            nome = obter_texto("Novo Nome: ", permitir_vazio=True)
            cpf = obter_texto("Novo CPF: ", permitir_vazio=True)
            data_nascimento = obter_texto("Nova Data de Nascimento (AAAA-MM-DD): ", permitir_vazio=True)
            is_flamengo = obter_sim_nao_opcional("Flamenguista? (S/N/Enter): ")
            telefone = obter_texto("Novo Telefone: ", permitir_vazio=True)
            num_convenio = obter_texto("Novo Convênio: ", permitir_vazio=True)
            alergias = obter_texto("Novas Alergias: ", permitir_vazio=True)
            grupo_sanguineo = obter_texto("Novo Grupo Sanguíneo: ", permitir_vazio=True)
            try:
                crud.atualizar_paciente(
                    session, id_paciente, nome=nome, cpf=cpf,
                    data_nascimento=data_nascimento, is_flamengo=is_flamengo,
                    telefone=telefone, num_convenio=num_convenio,
                    alergias=alergias, grupo_sanguineo=grupo_sanguineo,
                )
                print("\n[SUCESSO] Paciente atualizado com sucesso.")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except Exception as e:
                session.rollback()
                print(f"\n[ERRO] Não foi possível atualizar o paciente: {e}")

        elif opcao == "4":
            cabecalho("Remover Paciente")
            id_paciente = obter_int("Digite o ID do paciente: ")
            confirmar = obter_sim_nao(f"Remover paciente ID {id_paciente}? (S/N): ")
            if confirmar:
                try:
                    removido = crud.remover_pessoa(session, id_paciente)
                    if removido:
                        print("\n[SUCESSO] Paciente removido com sucesso.")
                    else:
                        print(f"\n[ERRO] Paciente ID {id_paciente} não encontrado.")
                except Exception as e:
                    session.rollback()
                    print(f"\n[ERRO] Não foi possível remover: {e}")


def gerenciar_profissionais(session: Session) -> None:
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
            tipo = obter_opcao("Tipo (P=Preceptor, R=Residente): ", ["p", "r", "P", "R"]).lower()
            if tipo == "p":
                tipo_str = "preceptor"
                info_tipo = obter_texto("Titulação (especialista/mestre/doutor/livre-docente): ")
            else:
                tipo_str = "residente"
                info_tipo = obter_texto("Ano de Residência (R1/R2/R3): ")
            try:
                id_gerado = crud.inserir_profissional(
                    session, nome, cpf, data_nascimento, is_flamengo, telefone,
                    crm, data_admissao, especialidade, tipo_str, info_tipo,
                )
                print(f"\n[SUCESSO] Profissional cadastrado com ID: {id_gerado}")
            except Exception as e:
                session.rollback()
                print(f"\n[ERRO] Não foi possível cadastrar o profissional: {e}")

        elif opcao == "2":
            cabecalho("Lista de Profissionais")
            profissionais = crud.listar_profissionais(session)
            if not profissionais:
                print("Nenhum profissional cadastrado.")
            else:
                for p in profissionais:
                    tipo = "Preceptor" if p.Preceptor else "Residente"
                    detalhe = (p.Preceptor.titulacao if p.Preceptor else p.Residente.ano_residencia) if (p.Preceptor or p.Residente) else ""
                    flamengo_str = "Sim" if p.Pessoa.is_flamengo == 1 else "Não"
                    print(
                        f"ID: {p.Pessoa.id_pessoa} | Nome: {p.Pessoa.nome} | CRM: {p.Profissional.crm} | "
                        f"Tipo: {tipo} ({detalhe}) | Especialidade: {p.Profissional.especialidade} | "
                        f"Flamengo: {flamengo_str}"
                    )

        elif opcao == "3":
            cabecalho("Atualizar Profissional")
            id_prof = obter_int("Digite o ID do profissional: ")
            print("Deixe vazio para não alterar.")
            nome = obter_texto("Novo Nome: ", permitir_vazio=True)
            cpf = obter_texto("Novo CPF: ", permitir_vazio=True)
            data_nascimento = obter_texto("Nova Data de Nascimento: ", permitir_vazio=True)
            is_flamengo = obter_sim_nao_opcional("Flamenguista? (S/N/Enter): ")
            telefone = obter_texto("Novo Telefone: ", permitir_vazio=True)
            crm = obter_texto("Novo CRM: ", permitir_vazio=True)
            data_admissao = obter_texto("Nova Data de Admissão: ", permitir_vazio=True)
            especialidade = obter_texto("Nova Especialidade: ", permitir_vazio=True)
            info_tipo = obter_texto("Novo Detalhe (Titulação ou Ano): ", permitir_vazio=True)
            try:
                crud.atualizar_profissional(
                    session, id_prof, nome=nome, cpf=cpf,
                    data_nascimento=data_nascimento, is_flamengo=is_flamengo,
                    telefone=telefone, crm=crm, data_admissao=data_admissao,
                    especialidade=especialidade, info_tipo=info_tipo,
                )
                print("\n[SUCESSO] Profissional atualizado com sucesso.")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except Exception as e:
                session.rollback()
                print(f"\n[ERRO] Não foi possível atualizar o profissional: {e}")

        elif opcao == "4":
            cabecalho("Remover Profissional")
            id_prof = obter_int("Digite o ID do profissional: ")
            confirmar = obter_sim_nao(f"Remover profissional ID {id_prof}? (S/N): ")
            if confirmar:
                try:
                    removido = crud.remover_pessoa(session, id_prof)
                    if removido:
                        print("\n[SUCESSO] Profissional removido com sucesso.")
                    else:
                        print(f"\n[ERRO] Profissional ID {id_prof} não encontrado.")
                except Exception as e:
                    session.rollback()
                    print(f"\n[ERRO] Não foi possível remover: {e}")


def gerenciar_atendimentos(session: Session) -> None:
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
            data_hora = obter_texto("Data e Hora (AAAA-MM-DD HH:MM:SS): ")
            duracao = obter_int("Duração (em minutos): ")
            id_paciente = obter_int("ID do Paciente: ")
            id_residente = obter_int("ID do Residente: ")
            id_preceptor = obter_int("ID do Preceptor: ")
            id_unidade = obter_int("ID da Unidade (opcional): ", permitir_vazio=True)
            try:
                id_gerado = crud.inserir_atendimento(
                    session, data_hora, duracao, id_paciente, id_residente, id_preceptor, id_unidade
                )
                print(f"\n[SUCESSO] Atendimento registrado com ID: {id_gerado}")
            except crud.RegistroNaoEncontrado as e:
                print(f"\n[ERRO] {e}")
            except Exception as e:
                session.rollback()
                print(f"\n[ERRO] Falha ao registrar atendimento: {e}")

        elif opcao == "2":
            cabecalho("Listar Atendimentos por Paciente")
            id_paciente = obter_int("Digite o ID do Paciente: ")
            atendimentos = crud.listar_atendimentos_por_paciente(session, id_paciente)
            if not atendimentos:
                print(f"Nenhum atendimento encontrado para o paciente ID {id_paciente}.")
            else:
                for a in atendimentos:
                    res_nome = a.residente.profissional.pessoa.nome if a.residente and a.residente.profissional else "N/A"
                    print(
                        f"ID: {a.id_atendimento} | Data/Hora: {a.data_hora} | "
                        f"Duração: {a.duracao_minutos} min | Residente: {res_nome}"
                    )


def visualizar_relatorios(session: Session) -> None:
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
            res = queries.ranking_residentes_por_atendimentos(session)
            for r in res:
                print(f"Residente: {r.nome_residente} | Total: {r.total_atendimentos}")

        elif opcao == "2":
            cabecalho("Preceptores com Atendimentos em Mês Específico")
            mes = obter_texto("Digite o mês/ano (AAAA-MM): ")
            minimo = obter_int("Mínimo de atendimentos (Enter para 1): ", permitir_vazio=True) or 1
            res = queries.preceptores_com_mais_de_n_atendimentos_no_mes(session, mes, minimo)
            if not res:
                print("Nenhum preceptor atendeu a esses critérios.")
            else:
                for r in res:
                    print(f"Preceptor: {r.nome_preceptor} | Atendimentos: {r.total_atendimentos}")

        elif opcao == "3":
            cabecalho("Plantões Escalados por Residente / Unidade")
            res = queries.plantoes_escalados_por_residente_por_unidade(session)
            for r in res:
                print(f"Unidade: {r.nome_unidade} | Residente: {r.nome_residente} | Plantões: {r.total_plantoes}")

        elif opcao == "4":
            cabecalho("Pacientes Sem Nenhum Procedimento de Risco ALTO")
            res = queries.pacientes_sem_procedimento_alto_risco(session)
            for r in res:
                print(f"Paciente: {r.nome_paciente} | Convênio: {r.num_convenio or 'N/A'}")

        elif opcao == "5":
            cabecalho("Duração Média de Atendimento por Residente")
            res = queries.tempo_medio_por_residente(session)
            for r in res:
                print(
                    f"Residente: {r.nome_residente} | "
                    f"Média: {float(r.media_duracao_minutos):.1f} min | "
                    f"Total: {r.total_atendimentos}"
                )


def menu_consultas_avancadas(session: Session) -> None:
    cabecalho("Consultas Avançadas (ORM — Etapa 2)")
    print("1. Preceptores que supervisionaram flamenguistas")
    print("2. Último atendimento por paciente (com procedimentos)")
    print("3. % procedimentos de alto risco por residente")
    opcao = obter_opcao("Opção: ", ["1", "2", "3"])

    if opcao == "1":
        nomes = queries.preceptores_que_supervisionaram_flamenguistas(session)
        cabecalho("Preceptores de Flamenguistas")
        for nome in nomes:
            print(f"  {nome}")

    elif opcao == "2":
        cabecalho("Último Atendimento por Paciente")
        atendimentos = queries.ultimo_atendimento_por_paciente(session)
        for a in atendimentos:
            procs = [pr.procedimento.nome for pr in a.procedimentos_realizados]
            res_nome = a.residente.profissional.pessoa.nome if a.residente and a.residente.profissional else "N/A"
            prec_nome = a.preceptor.profissional.pessoa.nome if a.preceptor and a.preceptor.profissional else "N/A"
            print(
                f"\n  Atendimento {a.id_atendimento} | {a.data_hora} | "
                f"Residente: {res_nome} | Preceptor: {prec_nome}"
            )
            print(f"  Procedimentos: {', '.join(procs) if procs else 'nenhum'}")

    elif opcao == "3":
        cabecalho("% Procedimentos de Alto Risco por Residente")
        rows = queries.percentual_alto_risco_por_residente(session)
        for row in rows:
            print(f"  {row.nome}: {float(row.percentual_alto_risco):.1f}%")


def menu_stored_procedures(session: Session) -> None:
    cabecalho("Stored Procedures — Etapa 2")
    print("1. sp_calcular_tempo_medio_espera")
    print("2. sp_reajustar_escala")
    print("3. sp_registrar_atendimento_completo (com procedimentos via JSON)")
    opcao = obter_opcao("Opção: ", ["1", "2", "3"])

    if opcao == "1":
        rows = session.execute(text("SELECT * FROM sp_calcular_tempo_medio_espera()")).fetchall()
        cabecalho("Tempo Médio de Espera por Unidade")
        for row in rows:
            print(f"  {row.nome_unidade}: {row.tempo_medio_minutos} min médios")

    elif opcao == "2":
        id_res = obter_int("ID do residente: ")
        dia_orig = obter_texto("Dia de origem: ")
        turno_orig = obter_texto("Turno de origem: ")
        dia_dest = obter_texto("Dia destino: ")
        turno_dest = obter_texto("Turno destino: ")
        try:
            n = session.execute(
                text("SELECT sp_reajustar_escala(:r, :do, :to, :dd, :td)"),
                {"r": id_res, "do": dia_orig, "to": turno_orig, "dd": dia_dest, "td": turno_dest},
            ).scalar()
            session.commit()
            print(f"\n[SUCESSO] {n} escala(s) reajustada(s).")
        except Exception as e:
            session.rollback()
            print(f"\n[ERRO] {e}")

    elif opcao == "3":
        import json
        data_hora = obter_texto("Data/Hora (AAAA-MM-DD HH:MM:SS): ")
        duracao = obter_int("Duração (minutos): ")
        id_paciente = obter_int("ID Paciente: ")
        id_residente = obter_int("ID Residente: ")
        id_preceptor = obter_int("ID Preceptor: ")
        id_unidade = obter_int("ID Unidade: ")
        n_procs = obter_int("Quantos procedimentos?: ")
        procs = []
        for i in range(n_procs):
            print(f"  Procedimento {i+1}:")
            procs.append({
                "id_procedimento": obter_int("    ID Procedimento: "),
                "quantidade": obter_int("    Quantidade: "),
                "tempo_real_minutos": obter_int("    Tempo real (min): "),
                "observacao": obter_texto("    Observação (opcional): ", permitir_vazio=True),
            })
        try:
            id_at = session.execute(
                text("""
                    SELECT sp_registrar_atendimento_completo(
                        CAST(:dh AS TIMESTAMP), :dur, :pac, :res, :prec, :uni, CAST(:procs AS JSON)
                    )
                """),
                {
                    "dh": data_hora, "dur": duracao, "pac": id_paciente,
                    "res": id_residente, "prec": id_preceptor, "uni": id_unidade,
                    "procs": json.dumps(procs),
                },
            ).scalar()
            session.commit()
            print(f"\n[SUCESSO] Atendimento registrado com ID: {id_at}")
        except Exception as e:
            session.rollback()
            print(f"\n[ERRO] {e}")


def menu_views(session: Session) -> None:
    cabecalho("Views — Etapa 2")
    print("1. vw_pacientes_internados")
    print("2. vw_residentes_sem_supervisor")
    print("3. vw_estatisticas_atendimentos_mensal")
    opcao = obter_opcao("Opção: ", ["1", "2", "3"])

    mapa = {
        "1": ("vw_pacientes_internados", ["id_pessoa", "nome", "unidade", "data_entrada"]),
        "2": ("vw_residentes_sem_supervisor", ["residente", "preceptor", "titulacao"]),
        "3": ("vw_estatisticas_atendimentos_mensal",
               ["mes", "unidade", "total_atendimentos", "media_duracao_min", "procedimento_mais_comum"]),
    }
    view, cols = mapa[opcao]
    cabecalho(view)
    rows = session.execute(text(f"SELECT * FROM {view}")).fetchall()
    if not rows:
        print("  Sem dados.")
    for row in rows:
        valores = "  |  ".join(str(getattr(row, c, '')) for c in cols)
        print(f"  {valores}")


def main() -> None:
    engine = db.get_engine()

    with Session(engine) as session:
        while True:
            cabecalho("Sistema de Gestão Hospitalar — Etapa 2")
            print("1. Gerenciar Pacientes")
            print("2. Gerenciar Profissionais")
            print("3. Gerenciar Atendimentos")
            print("4. Relatórios & Queries Analíticas")
            print("5. Consultas Avançadas (ORM)")
            print("6. Stored Procedures")
            print("7. Views")
            print("8. Resetar e Repovoar Banco de Dados")
            print("0. Sair do Sistema")

            opcao = obter_opcao("\nEscolha uma opção: ", ["0","1","2","3","4","5","6","7","8"])

            if opcao == "0":
                print("\nEncerrando sistema. Até logo!")
                break
            elif opcao == "1":
                gerenciar_pacientes(session)
            elif opcao == "2":
                gerenciar_profissionais(session)
            elif opcao == "3":
                gerenciar_atendimentos(session)
            elif opcao == "4":
                visualizar_relatorios(session)
            elif opcao == "5":
                menu_consultas_avancadas(session)
            elif opcao == "6":
                menu_stored_procedures(session)
            elif opcao == "7":
                menu_views(session)
            elif opcao == "8":
                confirmar = obter_sim_nao("\nResetar TODAS as tabelas e dados? (S/N): ")
                if confirmar:
                    try:
                        db.init_db(reset=True, seed=True)
                        print("\n[SUCESSO] Banco resetado e repovoado.")
                    except Exception as e:
                        print(f"\n[ERRO] {e}")


if __name__ == "__main__":
    main()
