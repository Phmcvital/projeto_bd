def ranking_residentes_por_atendimentos(conn) -> list:
    sql = """
        SELECT pe.nome AS nome_residente,
               COUNT(a.id_atendimento) AS total_atendimentos
        FROM RESIDENTE r
        JOIN PESSOA pe ON pe.id_pessoa = r.id_profissional
        LEFT JOIN ATENDIMENTO a ON a.id_residente = r.id_profissional
        GROUP BY r.id_profissional, pe.nome
        ORDER BY total_atendimentos DESC
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def preceptores_com_mais_de_n_atendimentos_no_mes(
    conn, ano_mes: str, minimo: int = 5
) -> list:
    sql = """
        SELECT pe.nome AS nome_preceptor,
               COUNT(a.id_atendimento) AS total_atendimentos
        FROM ATENDIMENTO a
        JOIN PESSOA pe ON pe.id_pessoa = a.id_preceptor
        WHERE substr(a.data_hora, 1, 7) = %s
        GROUP BY a.id_preceptor, pe.nome
        HAVING COUNT(a.id_atendimento) > %s
        ORDER BY total_atendimentos DESC
    """
    with conn.cursor() as cur:
        cur.execute(sql, (ano_mes, minimo))
        return cur.fetchall()


def plantoes_escalados_por_residente_por_unidade(conn) -> list:
    sql = """
        SELECT u.nome AS nome_unidade,
               pe.nome AS nome_residente,
               COUNT(e.id_escala) AS total_plantoes
        FROM ESCALA e
        JOIN UNIDADE u ON u.id_unidade = e.id_unidade
        JOIN PESSOA pe ON pe.id_pessoa = e.id_residente
        GROUP BY u.id_unidade, u.nome, e.id_residente, pe.nome
        ORDER BY u.nome, total_plantoes DESC
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()


def pacientes_sem_procedimento_alto_risco(conn) -> list:
    sql = """
        SELECT pe.nome AS nome_paciente,
               pa.num_convenio
        FROM PACIENTE pa
        JOIN PESSOA pe ON pe.id_pessoa = pa.id_pessoa
        WHERE pa.id_pessoa NOT IN (
            SELECT a.id_paciente
            FROM ATENDIMENTO a
            JOIN PROCEDIMENTO_REALIZADO pr ON pr.id_atendimento = a.id_atendimento
            JOIN PROCEDIMENTO p ON p.id_procedimento = pr.id_procedimento
            WHERE p.nivel_risco = 'ALTO'
        )
        ORDER BY pe.nome
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()
