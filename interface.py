import tkinter as tk
from tkinter import ttk, messagebox
from sqlalchemy import text

# Importa os módulos do seu projeto original
import db
import crud
import queries
import servicos_etapa2

class AppHospital:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestão Hospitalar - Completo (Etapas 1 e 2)")
        self.root.geometry("1100x700")
        self.root.configure(bg="#2c3e50")

        try:
            self.conn = db.get_session()
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha de conexão:\n{e}")
            self.root.destroy()
            return

        # ==========================================
        # ESTRUTURA DA TELA (Layout Principal)
        # ==========================================
        self.frame_menu = tk.Frame(self.root, width=220, bg="#1a252f")
        self.frame_menu.pack(side=tk.LEFT, fill=tk.Y)

        self.frame_conteudo = tk.Frame(self.root, bg="#ecf0f1")
        self.frame_conteudo.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.construir_menu()
        self.mostrar_inicio()

    def construir_menu(self):
        estilo_btn = {"bg": "#34495e", "fg": "white", "font": ("Arial", 10), "bd": 0, "pady": 5}
        
        tk.Label(self.frame_menu, text="ETAPA 1 (CRUD & Relatórios)", bg="#1a252f", fg="#f1c40f", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        tk.Button(self.frame_menu, text="Gerenciar Pacientes", command=self.mostrar_pacientes, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Gerenciar Profissionais", command=self.mostrar_profissionais, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Gerenciar Atendimentos", command=self.mostrar_atendimentos_básico, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Relatórios Etapa 1", command=self.mostrar_relatorios_e1, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)

        tk.Label(self.frame_menu, text="ETAPA 2 (Avançado)", bg="#1a252f", fg="#3498db", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        tk.Button(self.frame_menu, text="Registrar Atend. (SP)", command=self.mostrar_form_atendimento_sp, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Reajustar Escala (SP)", command=self.mostrar_form_escala, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Tempo de Espera (SP)", command=self.mostrar_tempo_espera, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        
        tk.Label(self.frame_menu, text="ANALÍTICO", bg="#1a252f", fg="#e74c3c", font=("Arial", 10, "bold")).pack(pady=(20, 5))
        tk.Button(self.frame_menu, text="Consultar Views", command=self.mostrar_views, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Auditoria (Triggers)", command=self.mostrar_auditoria, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)
        tk.Button(self.frame_menu, text="Consultas ORM", command=self.mostrar_consultas_orm, **estilo_btn).pack(fill=tk.X, padx=10, pady=2)

    # ==========================================
    # BUSCADORES DE DADOS (Ordenados por ID)
    # ==========================================
    def get_opcoes_pacientes(self):
        try:
            # listar_pacientes já ordena por Paciente.id_pessoa no CRUD
            return [f"{p['id_pessoa']} - {p['nome']}" for p in crud.listar_pacientes(self.conn)]
        except: return []

    def get_opcoes_residentes(self):
        try:
            # listar_profissionais já ordena por Profissional.id_pessoa no CRUD
            return [f"{p['id_pessoa']} - {p['nome']}" for p in crud.listar_profissionais(self.conn) if p['tipo'] == 'residente']
        except: return []

    def get_opcoes_preceptores(self):
        try:
            return [f"{p['id_pessoa']} - {p['nome']}" for p in crud.listar_profissionais(self.conn) if p['tipo'] == 'preceptor']
        except: return []

    def get_opcoes_unidades(self):
        try:
            # Como listar_unidades ordenava por Nome no CRUD, forçamos a ordenação pelo ID aqui
            unidades = crud.listar_unidades(self.conn)
            unidades_ordenadas = sorted(unidades, key=lambda x: x['id_unidade'])
            return [f"{u['id_unidade']} - {u['nome']}" for u in unidades_ordenadas]
        except: return []

    def get_opcoes_procedimentos(self):
        try:
            # Fazemos o SELECT forçando o ORDER BY pelo id_procedimento
            res = self.conn.execute(text("SELECT id_procedimento, nome FROM procedimento ORDER BY id_procedimento")).fetchall()
            return [f"{r[0]} - {r[1]}" for r in res]
        except: return []

    # ==========================================
    # UTILITÁRIOS DA INTERFACE
    # ==========================================
    def limpar_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def desenhar_tabela_dinamica(self, parent_frame, dados):
        for widget in parent_frame.winfo_children():
            widget.destroy()
            
        if not dados:
            tk.Label(parent_frame, text="Nenhum dado encontrado.", bg="#ecf0f1").pack(pady=20)
            return

        colunas = list(dados[0].keys())
        frame_tabela = tk.Frame(parent_frame)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scroll_y = ttk.Scrollbar(frame_tabela)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x = ttk.Scrollbar(frame_tabela, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", 
                              yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=tabela.yview)
        scroll_x.config(command=tabela.xview)

        for col in colunas:
            tabela.heading(col, text=str(col).replace("_", " ").upper())
            tabela.column(col, width=120, anchor=tk.CENTER)
        tabela.pack(fill=tk.BOTH, expand=True)

        for linha in dados:
            tabela.insert("", tk.END, values=[str(v) if v is not None else "" for v in linha.values()])

    def criar_formulario(self, parent_frame, config_campos, txt_botao, callback_submit):
        """Gera formulários com Textos ou Menus Suspensos vazios inicialmente."""
        entradas = {}
        for i, (label_text, config) in enumerate(config_campos.items()):
            tk.Label(parent_frame, text=label_text, bg="#ecf0f1").grid(row=i, column=0, sticky="e", pady=5, padx=5)
            
            if config.get("tipo") == "combo":
                ent = ttk.Combobox(parent_frame, values=config.get("valores", []), width=40, state="readonly")
                # Garante que todo Combobox comece limpo (vazio), sem pré-selecionar o primeiro da lista
                ent.set("") 
            else:
                ent = tk.Entry(parent_frame, width=43)
            
            ent.grid(row=i, column=1, pady=5, padx=5)
            entradas[label_text] = ent

        def submit():
            valores = {}
            for k, v in entradas.items():
                val = v.get().strip()
                # Se for um Combobox e tiver formato "ID - Nome", pega só o ID.
                if config_campos[k].get("tipo") == "combo" and " - " in val:
                    val = val.split(" - ")[0]
                valores[k] = val or None
            callback_submit(valores)

        tk.Button(parent_frame, text=txt_botao, bg="#2980b9", fg="white", command=submit).grid(row=len(config_campos), columnspan=2, pady=15)

    def mostrar_inicio(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Bem-vindo ao Sistema Hospitalar", font=("Arial", 18, "bold"), bg="#ecf0f1").pack(pady=30)
        tk.Label(self.frame_conteudo, text="Os menus de seleção agora iniciam vazios e estão ordenados por ID.", bg="#ecf0f1").pack()

    # ==========================================
    # FUNÇÕES DA ETAPA 1 (CRUD)
    # ==========================================
    def mostrar_pacientes(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Gerenciar Pacientes", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        abas = ttk.Notebook(self.frame_conteudo)
        abas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba 1: Listar
        aba_listar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_listar, text="Listar Pacientes")
        try:
            self.desenhar_tabela_dinamica(aba_listar, crud.listar_pacientes(self.conn))
        except Exception as e:
            tk.Label(aba_listar, text=str(e)).pack()

        # Aba 2: Cadastrar
        aba_cadastrar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_cadastrar, text="Cadastrar Novo")
        def salvar_paciente(vals):
            try:
                # Validação para evitar erro ao converter None para inteiro se não for preenchido
                is_flamengo_val = int(vals["É Flamengo? (1=Sim, 0=Não):"]) if vals["É Flamengo? (1=Sim, 0=Não):"] else 0
                
                crud.inserir_paciente(self.conn, vals["Nome:"], vals["CPF:"], vals["Data Nasc (YYYY-MM-DD):"], 
                                      is_flamengo_val, vals["Telefone:"], vals["Convênio:"], 
                                      vals["Alergias:"], vals["Grupo Sanguíneo:"])
                messagebox.showinfo("Sucesso", "Paciente cadastrado!")
                self.mostrar_pacientes()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Erro", f"Por favor, verifique se todos os campos obrigatórios foram preenchidos corretamente.\nDetalhes: {e}")

        campos_paciente = {
            "Nome:": {"tipo": "entry"}, "CPF:": {"tipo": "entry"}, "Data Nasc (YYYY-MM-DD):": {"tipo": "entry"},
            "É Flamengo? (1=Sim, 0=Não):": {"tipo": "combo", "valores": ["1 - Sim", "0 - Não"]}, "Telefone:": {"tipo": "entry"},
            "Convênio:": {"tipo": "entry"}, "Alergias:": {"tipo": "entry"},
            "Grupo Sanguíneo:": {"tipo": "combo", "valores": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]}
        }
        self.criar_formulario(aba_cadastrar, campos_paciente, "Salvar Paciente", salvar_paciente)

        # Aba 3: Remover
        aba_remover = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_remover, text="Remover Paciente")
        def remover_paciente(vals):
            try:
                if not vals["Paciente:"]: raise ValueError("Selecione um paciente.")
                sucesso = crud.remover_pessoa(self.conn, int(vals["Paciente:"]))
                if sucesso: messagebox.showinfo("Sucesso", "Paciente removido!")
                else: messagebox.showwarning("Aviso", "Paciente não encontrado.")
                self.mostrar_pacientes()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Erro", str(e))
        self.criar_formulario(aba_remover, {"Paciente:": {"tipo": "combo", "valores": self.get_opcoes_pacientes()}}, "Remover", remover_paciente)

    def mostrar_profissionais(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Gerenciar Profissionais", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        abas = ttk.Notebook(self.frame_conteudo)
        abas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        aba_listar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_listar, text="Listar Profissionais")
        try:
            self.desenhar_tabela_dinamica(aba_listar, crud.listar_profissionais(self.conn))
        except Exception as e:
            tk.Label(aba_listar, text=str(e)).pack()

        aba_cadastrar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_cadastrar, text="Cadastrar Novo")
        def salvar_prof(vals):
            try:
                flamengo_val = int(vals["Flamengo (1/0):"]) if vals["Flamengo (1/0):"] else 0
                crud.inserir_profissional(self.conn, vals["Nome:"], vals["CPF:"], vals["Nascimento (YYYY-MM-DD):"], 
                                          flamengo_val, vals["Telefone:"], vals["CRM:"], vals["Admissão (YYYY-MM-DD):"],
                                          vals["Especialidade:"], vals["Tipo (preceptor / residente):"], vals["Titulação ou Ano (R1, R2):"])
                messagebox.showinfo("Sucesso", "Profissional cadastrado!")
                self.mostrar_profissionais()
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Erro", f"Por favor, verifique se todos os campos obrigatórios estão preenchidos.\nDetalhes: {e}")

        campos_prof = {
            "Nome:": {"tipo": "entry"}, "CPF:": {"tipo": "entry"}, "Nascimento (YYYY-MM-DD):": {"tipo": "entry"},
            "Flamengo (1/0):": {"tipo": "combo", "valores": ["1 - Sim", "0 - Não"]}, "Telefone:": {"tipo": "entry"},
            "CRM:": {"tipo": "entry"}, "Admissão (YYYY-MM-DD):": {"tipo": "entry"}, "Especialidade:": {"tipo": "entry"},
            "Tipo (preceptor / residente):": {"tipo": "combo", "valores": ["preceptor", "residente"]},
            "Titulação ou Ano (R1, R2):": {"tipo": "entry"}
        }
        self.criar_formulario(aba_cadastrar, campos_prof, "Salvar Profissional", salvar_prof)

    def mostrar_atendimentos_básico(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Atendimentos (Etapa 1)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        abas = ttk.Notebook(self.frame_conteudo)
        abas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Aba 1: Buscar
        aba_listar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_listar, text="Listar por Paciente")
        def buscar_atend(vals):
            try:
                if not vals["Paciente:"]: raise ValueError("Selecione um paciente na lista.")
                self.desenhar_tabela_dinamica(frame_tabela_atend, crud.listar_atendimentos_por_paciente(self.conn, int(vals["Paciente:"])))
            except Exception as e: messagebox.showerror("Erro", str(e))
        
        f_busca = tk.Frame(aba_listar, bg="#ecf0f1")
        f_busca.pack(pady=5)
        self.criar_formulario(f_busca, {"Paciente:": {"tipo": "combo", "valores": self.get_opcoes_pacientes()}}, "Buscar", buscar_atend)
        frame_tabela_atend = tk.Frame(aba_listar, bg="#ecf0f1")
        frame_tabela_atend.pack(fill=tk.BOTH, expand=True)

        # Aba 2: Cadastrar
        aba_cadastrar = tk.Frame(abas, bg="#ecf0f1")
        abas.add(aba_cadastrar, text="Registrar Simples (S/ Transação)")
        def salvar_atend(vals):
            try:
                for k, v in vals.items():
                    if not v: raise ValueError(f"O campo '{k}' deve ser preenchido.")
                
                crud.inserir_atendimento(self.conn, vals["Data/Hora (YYYY-MM-DD HH:MM):"], int(vals["Duração (min):"]), 
                                         int(vals["Paciente:"]), int(vals["Residente:"]), int(vals["Preceptor:"]), int(vals["Unidade:"]))
                messagebox.showinfo("Sucesso", "Atendimento cadastrado!")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Erro", str(e))

        campos_atend = {
            "Data/Hora (YYYY-MM-DD HH:MM):": {"tipo": "entry"}, "Duração (min):": {"tipo": "entry"},
            "Paciente:": {"tipo": "combo", "valores": self.get_opcoes_pacientes()},
            "Residente:": {"tipo": "combo", "valores": self.get_opcoes_residentes()},
            "Preceptor:": {"tipo": "combo", "valores": self.get_opcoes_preceptores()},
            "Unidade:": {"tipo": "combo", "valores": self.get_opcoes_unidades()}
        }
        self.criar_formulario(aba_cadastrar, campos_atend, "Salvar Atendimento", salvar_atend)

    def mostrar_relatorios_e1(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Relatórios Analíticos (Etapa 1)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        f_top = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_top.pack()
        
        opcoes = ["Ranking de Residentes", "Plantões por Unidade/Residente", "Pacientes s/ Procedimento ALTO", "Duração Média por Residente", "Preceptores no Mês"]
        combo = ttk.Combobox(f_top, values=opcoes, state="readonly", width=40)
        combo.set(opcoes[0])
        combo.pack(side=tk.LEFT, padx=10)

        f_inputs = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_inputs.pack(pady=5)
        tk.Label(f_inputs, text="Mês/Ano (YYYY-MM) - Só para Preceptores:", bg="#ecf0f1").pack(side=tk.LEFT)
        ent_mes = tk.Entry(f_inputs, width=10)
        ent_mes.pack(side=tk.LEFT, padx=5)

        frame_tabela = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        frame_tabela.pack(fill=tk.BOTH, expand=True)

        def carregar():
            try:
                sel = combo.get()
                if sel == opcoes[0]: dados = queries.ranking_residentes_por_atendimentos(self.conn)
                elif sel == opcoes[1]: dados = queries.plantoes_escalados_por_residente_por_unidade(self.conn)
                elif sel == opcoes[2]: dados = queries.pacientes_sem_procedimento_alto_risco(self.conn)
                elif sel == opcoes[3]: dados = crud.tempo_medio_por_residente(self.conn)
                elif sel == opcoes[4]: 
                    if not ent_mes.get(): raise ValueError("Preencha o campo de mês (ex: 2026-04)")
                    dados = queries.preceptores_com_mais_de_n_atendimentos_no_mes(self.conn, ent_mes.get(), 1)
                
                self.desenhar_tabela_dinamica(frame_tabela, dados)
            except Exception as e: messagebox.showerror("Erro", str(e))

        tk.Button(f_top, text="Gerar Relatório", command=carregar).pack(side=tk.LEFT)

    # ==========================================
    # FUNÇÕES DA ETAPA 2 (Procedures e Views)
    # ==========================================
    def mostrar_tempo_espera(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Tempo Médio de Espera (SP)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        frame_tabela = tk.Frame(self.frame_conteudo)
        frame_tabela.pack(fill=tk.BOTH, expand=True)
        try:
            self.desenhar_tabela_dinamica(frame_tabela, servicos_etapa2.calcular_tempo_medio_espera(self.conn))
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Erro", str(e))

    def mostrar_form_escala(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Reajustar Escala (Stored Procedure)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=20)
        f_form = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_form.pack(pady=10)

        def submeter(v):
            try:
                for k, val in v.items():
                    if not val: raise ValueError(f"O campo '{k}' é obrigatório.")
                servicos_etapa2.reajustar_escala(self.conn, int(v["Residente:"]), v["Dia Origem:"], v["Turno Origem:"], v["Dia Destino:"], v["Turno Destino:"])
                messagebox.showinfo("Sucesso", "Escala reajustada!")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Erro de Regra de Negócio", str(e))
        
        campos_escala = {
            "Residente:": {"tipo": "combo", "valores": self.get_opcoes_residentes()},
            "Dia Origem:": {"tipo": "combo", "valores": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]},
            "Turno Origem:": {"tipo": "combo", "valores": ["manha", "tarde", "noite"]},
            "Dia Destino:": {"tipo": "combo", "valores": ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]},
            "Turno Destino:": {"tipo": "combo", "valores": ["manha", "tarde", "noite"]}
        }
        self.criar_formulario(f_form, campos_escala, "Executar Reajuste", submeter)

    def mostrar_form_atendimento_sp(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Registro Completo c/ Transação (SP)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        tk.Label(self.frame_conteudo, text="(Registra atendimento e reverte tudo caso falhe)", bg="#ecf0f1").pack()
        f_form = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_form.pack(pady=10)

        def submeter(v):
            try:
                for k, val in v.items():
                    if not val: raise ValueError(f"O campo '{k}' é obrigatório para registrar a transação.")
                    
                dados_atend = {"data_hora": v["Data/Hora:"], "duracao_minutos": int(v["Duração (min):"]), "id_paciente": int(v["Paciente:"]), "id_residente": int(v["Residente:"]), "id_preceptor": int(v["Preceptor:"]), "id_unidade": int(v["Unidade:"])}
                proc_lote = [{"id_procedimento": int(v["Procedimento:"]), "quantidade": 1, "data_hora_inicio": v["Data/Hora:"], "tempo_real_minutos": int(v["Tempo Real Proc (min):"]), "observacao": "Via App", "faturado": False}]
                
                servicos_etapa2.registrar_atendimento_completo(self.conn, dados_atend, proc_lote)
                messagebox.showinfo("Sucesso", "Transação concluída: Atendimento registrado.")
            except Exception as e:
                self.conn.rollback()
                messagebox.showerror("Rollback Executado", str(e))

        campos_atend_sp = {
            "Data/Hora:": {"tipo": "entry"}, "Duração (min):": {"tipo": "entry"},
            "Paciente:": {"tipo": "combo", "valores": self.get_opcoes_pacientes()},
            "Residente:": {"tipo": "combo", "valores": self.get_opcoes_residentes()},
            "Preceptor:": {"tipo": "combo", "valores": self.get_opcoes_preceptores()},
            "Unidade:": {"tipo": "combo", "valores": self.get_opcoes_unidades()},
            "Procedimento:": {"tipo": "combo", "valores": self.get_opcoes_procedimentos()},
            "Tempo Real Proc (min):": {"tipo": "entry"}
        }
        self.criar_formulario(f_form, campos_atend_sp, "Salvar Tudo", submeter)

    def mostrar_views(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Consultar Views do Banco", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        f_top = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_top.pack()
        
        # Este Combobox das views também inicia vazio
        combo = ttk.Combobox(f_top, values=["internados", "sem_supervisor", "estatisticas"], state="readonly")
        combo.set("")
        combo.pack(side=tk.LEFT, padx=10)
        
        frame_tabela = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        frame_tabela.pack(fill=tk.BOTH, expand=True)

        def carregar():
            try:
                if not combo.get(): raise ValueError("Selecione uma View no menu suspenso.")
                self.desenhar_tabela_dinamica(frame_tabela, servicos_etapa2.consultar_view(self.conn, combo.get()))
            except Exception as e: messagebox.showerror("Erro", str(e))
        tk.Button(f_top, text="Carregar", command=carregar).pack(side=tk.LEFT)

    def mostrar_auditoria(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Auditoria de Atendimentos (Triggers)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        frame_tabela = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        frame_tabela.pack(fill=tk.BOTH, expand=True)
        try:
            self.desenhar_tabela_dinamica(frame_tabela, servicos_etapa2.listar_auditoria(self.conn, limite=30))
        except Exception as e: messagebox.showerror("Erro", str(e))

    def mostrar_consultas_orm(self):
        self.limpar_conteudo()
        tk.Label(self.frame_conteudo, text="Consultas Avançadas (ORM SQLAlchemy)", font=("Arial", 14, "bold"), bg="#ecf0f1").pack(pady=10)
        f_top = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        f_top.pack()
        opcoes = ["Preceptores de Pacientes Flamenguistas", "Último Atendimento de Cada Paciente", "Percentual de Alto Risco por Residente"]
        combo = ttk.Combobox(f_top, values=opcoes, state="readonly", width=40)
        combo.set("")
        combo.pack(side=tk.LEFT, padx=10)
        frame_tabela = tk.Frame(self.frame_conteudo, bg="#ecf0f1")
        frame_tabela.pack(fill=tk.BOTH, expand=True)

        def carregar():
            try:
                sel = combo.get()
                if not sel: raise ValueError("Selecione uma query no menu suspenso.")
                if sel == opcoes[0]: dados = queries.preceptores_de_pacientes_flamenguistas(self.conn)
                elif sel == opcoes[1]: dados = queries.ultimo_atendimento_por_paciente(self.conn)
                else: dados = queries.percentual_alto_risco_por_residente(self.conn)
                self.desenhar_tabela_dinamica(frame_tabela, dados)
            except Exception as e: messagebox.showerror("Erro", str(e))
        tk.Button(f_top, text="Executar Query", command=carregar).pack(side=tk.LEFT)

if __name__ == "__main__":
    janela = tk.Tk()
    app = AppHospital(janela)
    janela.mainloop()