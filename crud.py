class RegistroNaoEncontrado(Exception):
    pass


def inserir_atendimento(
    conn,
    data_hora: str,
    duracao_minutos: int,
    id_paciente: int,
    id_residente: int,
    id_preceptor: int,
) -> int:
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM PACIENTE WHERE id_pessoa = %s", (id_paciente,))
        if cur.fetchone() is None:
            raise RegistroNaoEncontrado(f"Paciente {id_paciente} não existe.")
        
        cur.execute("SELECT 1 FROM RESIDENTE WHERE id_profissional = %s", (id_residente,))
        if cur.fetchone() is None:
            raise RegistroNaoEncontrado(f"Residente {id_residente} não existe.")
        
        cur.execute("SELECT 1 FROM PRECEPTOR WHERE id_profissional = %s", (id_preceptor,))
        if cur.fetchone() is None:
            raise RegistroNaoEncontrado(f"Preceptor {id_preceptor} não existe.")

        cur.execute(
            """
            INSERT INTO ATENDIMENTO (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_atendimento
            """,
            (data_hora, duracao_minutos, id_paciente, id_residente, id_preceptor),
        )
        novo_id = cur.fetchone()[0]
    conn.commit()
    return novo_id


def listar_atendimentos_por_paciente(conn, id_paciente: int) -> list:
    sql = """
        SELECT a.id_atendimento,
            a.data_hora,
            a.duracao_minutos,
            pr.nome AS nome_residente,
            pc.nome AS nome_preceptor
        FROM ATENDIMENTO a
        JOIN PROFISSIONAL prof_res ON prof_res.id_pessoa = a.id_residente
        JOIN PESSOA pr ON pr.id_pessoa = a.id_residente
        JOIN PESSOA pc ON pc.id_pessoa = a.id_preceptor
        WHERE a.id_paciente = %s
        ORDER BY a.data_hora ASC
    """
    with conn.cursor() as cur:
        cur.execute(sql, (id_paciente,))
        return cur.fetchall()


def listar_procedimentos_de_atendimento(conn, id_atendimento: int) -> list:
    sql = """
        SELECT p.nome AS nome_procedimento,
            pr.quantidade,
            pr.tempo_real_minutos,
            pr.observacao
        FROM PROCEDIMENTO_REALIZADO pr
        JOIN PROCEDIMENTO p ON p.id_procedimento = pr.id_procedimento
        WHERE pr.id_atendimento = %s
        ORDER BY p.nome
    """
    with conn.cursor() as cur:
        cur.execute(sql, (id_atendimento,))
        return cur.fetchall()


def atualizar_paciente(
    conn,
    id_paciente: int,
    nome: str | None = None,
    cpf: str | None = None,
    data_nascimento: str | None = None,
    is_flamengo: int | None = None,
    telefone: str | None = None,
    num_convenio: str | None = None,
    alergias: str | None = None,
    grupo_sanguineo: str | None = None,
) -> None:
    with conn.cursor() as cur:
        # Verificar se paciente existe
        cur.execute("SELECT 1 FROM PACIENTE WHERE id_pessoa = %s", (id_paciente,))
        if cur.fetchone() is None:
            raise RegistroNaoEncontrado(f"Paciente {id_paciente} não existe.")

        # Atualizar PESSOA
        campos_pessoa = []
        valores_pessoa = []
        if nome is not None:
            campos_pessoa.append("nome = %s")
            valores_pessoa.append(nome)
        if cpf is not None:
            campos_pessoa.append("cpf = %s")
            valores_pessoa.append(cpf)
        if data_nascimento is not None:
            campos_pessoa.append("data_nascimento = %s")
            valores_pessoa.append(data_nascimento)
        if is_flamengo is not None:
            campos_pessoa.append("is_flamengo = %s")
            valores_pessoa.append(is_flamengo)
        if telefone is not None:
            campos_pessoa.append("telefone = %s")
            valores_pessoa.append(telefone)

        if campos_pessoa:
            valores_pessoa.append(id_paciente)
            sql_pessoa = f"UPDATE PESSOA SET {', '.join(campos_pessoa)} WHERE id_pessoa = %s"
            cur.execute(sql_pessoa, valores_pessoa)

        # Atualizar PACIENTE
        campos_paciente = []
        valores_paciente = []
        if num_convenio is not None:
            campos_paciente.append("num_convenio = %s")
            valores_paciente.append(num_convenio)
        if alergias is not None:
            campos_paciente.append("alergias = %s")
            valores_paciente.append(alergias)
        if grupo_sanguineo is not None:
            campos_paciente.append("grupo_sanguineo = %s")
            valores_paciente.append(grupo_sanguineo)

        if campos_paciente:
            valores_paciente.append(id_paciente)
            sql_paciente = f"UPDATE PACIENTE SET {', '.join(campos_paciente)} WHERE id_pessoa = %s"
            cur.execute(sql_paciente, valores_paciente)
            
    conn.commit()


def atualizar_profissional(
    conn,
    id_profissional: int,
    nome: str | None = None,
    cpf: str | None = None,
    data_nascimento: str | None = None,
    is_flamengo: int | None = None,
    telefone: str | None = None,
    crm: str | None = None,
    data_admissao: str | None = None,
    especialidade: str | None = None,
    info_tipo: str | None = None,
) -> None:
    with conn.cursor() as cur:
        # Verificar se profissional existe e descobrir o tipo dele
        cur.execute(
            """
            SELECT 
                CASE 
                    WHEN prec.id_profissional IS NOT NULL THEN 'preceptor'
                    WHEN res.id_profissional IS NOT NULL THEN 'residente'
                    ELSE NULL
                END AS tipo
            FROM PROFISSIONAL pr
            LEFT JOIN PRECEPTOR prec ON prec.id_profissional = pr.id_pessoa
            LEFT JOIN RESIDENTE res ON res.id_profissional = pr.id_pessoa
            WHERE pr.id_pessoa = %s
            """,
            (id_profissional,)
        )
        row = cur.fetchone()
        if row is None or row["tipo"] is None:
            raise RegistroNaoEncontrado(f"Profissional {id_profissional} não existe.")

        tipo = row["tipo"]

        # Atualizar PESSOA
        campos_pessoa = []
        valores_pessoa = []
        if nome is not None:
            campos_pessoa.append("nome = %s")
            valores_pessoa.append(nome)
        if cpf is not None:
            campos_pessoa.append("cpf = %s")
            valores_pessoa.append(cpf)
        if data_nascimento is not None:
            campos_pessoa.append("data_nascimento = %s")
            valores_pessoa.append(data_nascimento)
        if is_flamengo is not None:
            campos_pessoa.append("is_flamengo = %s")
            valores_pessoa.append(is_flamengo)
        if telefone is not None:
            campos_pessoa.append("telefone = %s")
            valores_pessoa.append(telefone)

        if campos_pessoa:
            valores_pessoa.append(id_profissional)
            sql_pessoa = f"UPDATE PESSOA SET {', '.join(campos_pessoa)} WHERE id_pessoa = %s"
            cur.execute(sql_pessoa, valores_pessoa)

        # Atualizar PROFISSIONAL
        campos_prof = []
        valores_prof = []
        if crm is not None:
            campos_prof.append("crm = %s")
            valores_prof.append(crm)
        if data_admissao is not None:
            campos_prof.append("data_admissao = %s")
            valores_prof.append(data_admissao)
        if especialidade is not None:
            campos_prof.append("especialidade = %s")
            valores_prof.append(especialidade)

        if campos_prof:
            valores_prof.append(id_profissional)
            sql_prof = f"UPDATE PROFISSIONAL SET {', '.join(campos_prof)} WHERE id_pessoa = %s"
            cur.execute(sql_prof, valores_prof)

        # Atualizar tipo específico
        if info_tipo is not None:
            if tipo == "preceptor":
                cur.execute(
                    "UPDATE PRECEPTOR SET titulacao = %s WHERE id_profissional = %s",
                    (info_tipo, id_profissional),
                )
            elif tipo == "residente":
                cur.execute(
                    "UPDATE RESIDENTE SET ano_residencia = %s WHERE id_profissional = %s",
                    (info_tipo, id_profissional),
                )
                
    conn.commit()


def remover_procedimento_realizado(conn, id_atendimento: int, id_procedimento: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT faturado FROM PROCEDIMENTO_REALIZADO
            WHERE id_atendimento = %s AND id_procedimento = %s
            """,
            (id_atendimento, id_procedimento),
        )
        row = cur.fetchone()

        if row is None:
            raise RegistroNaoEncontrado("Procedimento realizado não encontrado para esse atendimento.")

        if row["faturado"] == 1:
            return False 

        cur.execute(
            "DELETE FROM PROCEDIMENTO_REALIZADO WHERE id_atendimento = %s AND id_procedimento = %s",
            (id_atendimento, id_procedimento),
        )
    conn.commit()
    return True


def tempo_medio_por_residente(conn) -> list:
    sql = """
        SELECT pe.id_pessoa AS id_residente,
            pe.nome AS nome_residente,
            AVG(a.duracao_minutos) AS media_duracao_minutos,
            COUNT(a.id_atendimento) AS total_atendimentos
        FROM ATENDIMENTO a
        JOIN PESSOA pe ON pe.id_pessoa = a.id_residente
        GROUP BY pe.id_pessoa, pe.nome
        ORDER BY media_duracao_minutos DESC
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


# --- NOVAS OPERAÇÕES CRUD PARA A CLI ---

def inserir_paciente(
    conn,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone: str | None,
    num_convenio: str | None,
    alergias: str | None,
    grupo_sanguineo: str | None,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_pessoa
            """,
            (nome, cpf, data_nascimento, is_flamengo, telefone),
        )
        id_pessoa = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO PACIENTE (id_pessoa, num_convenio, alergias, grupo_sanguineo)
            VALUES (%s, %s, %s, %s)
            """,
            (id_pessoa, num_convenio, alergias, grupo_sanguineo),
        )
    conn.commit()
    return id_pessoa


def listar_pacientes(conn) -> list:
    sql = """
        SELECT p.id_pessoa, p.nome, p.cpf, p.data_nascimento, p.is_flamengo, p.telefone,
               pa.num_convenio, pa.alergias, pa.grupo_sanguineo
        FROM PACIENTE pa
        JOIN PESSOA p ON p.id_pessoa = pa.id_pessoa
        ORDER BY p.nome
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def inserir_profissional(
    conn,
    nome: str,
    cpf: str,
    data_nascimento: str,
    is_flamengo: int,
    telefone: str | None,
    crm: str,
    data_admissao: str,
    especialidade: str,
    tipo: str,
    info_tipo: str,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO PESSOA (nome, cpf, data_nascimento, is_flamengo, telefone)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id_pessoa
            """,
            (nome, cpf, data_nascimento, is_flamengo, telefone),
        )
        id_pessoa = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO PROFISSIONAL (id_pessoa, crm, data_admissao, especialidade)
            VALUES (%s, %s, %s, %s)
            """,
            (id_pessoa, crm, data_admissao, especialidade),
        )

        if tipo.lower() == "preceptor":
            cur.execute(
                """
                INSERT INTO PRECEPTOR (id_profissional, titulacao)
                VALUES (%s, %s)
                """,
                (id_pessoa, info_tipo),
            )
        elif tipo.lower() == "residente":
            cur.execute(
                """
                INSERT INTO RESIDENTE (id_profissional, ano_residencia)
                VALUES (%s, %s)
                """,
                (id_pessoa, info_tipo),
            )
        else:
            raise ValueError("Tipo inválido. Deve ser 'preceptor' ou 'residente'.")
    conn.commit()
    return id_pessoa


def listar_profissionais(conn) -> list:
    sql = """
        SELECT p.id_pessoa, p.nome, p.cpf, p.data_nascimento, p.is_flamengo, p.telefone,
               pr.crm, pr.data_admissao, pr.especialidade,
               CASE 
                   WHEN prec.id_profissional IS NOT NULL THEN 'Preceptor'
                   WHEN res.id_profissional IS NOT NULL THEN 'Residente'
                   ELSE 'Geral'
               END AS tipo,
               COALESCE(prec.titulacao, res.ano_residencia, '') AS detalhe
        FROM PROFISSIONAL pr
        JOIN PESSOA p ON p.id_pessoa = pr.id_pessoa
        LEFT JOIN PRECEPTOR prec ON prec.id_profissional = pr.id_pessoa
        LEFT JOIN RESIDENTE res ON res.id_profissional = pr.id_pessoa
        ORDER BY p.nome
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def remover_pessoa(conn, id_pessoa: int) -> bool:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM PESSOA WHERE id_pessoa = %s", (id_pessoa,))
        linhas_afetadas = cur.rowcount
    conn.commit()
    return linhas_afetadas > 0


def listar_unidades(conn) -> list:
    sql = "SELECT id_unidade, nome, tipo, capacidade_leitos FROM UNIDADE ORDER BY nome"
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
