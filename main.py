from cadastro import Cadastro
from tads import Fila, Pilha
from Heap import MinHeap
from arvore import ArvoreB as A
from arvoreb import ArvoreB as B

print("=== CENTRAL DE RESERVAS - Setor: Correios ===")

def _data_para_chave(s):
    """'DD/MM/YYYY' → inteiro YYYYMMDD ordenável cronologicamente.
    Retorna None se a data for vazia/inválida."""
    try:
        d, m, a = str(s).strip().split("/")
        return int(a) * 10000 + int(m) * 100 + int(d)
    except (ValueError, AttributeError):
        return None

def _para_iso(s):
    """'DD/MM/YYYY' → 'YYYY-MM-DD' (comparável lexicograficamente)."""
    try:
        d, m, a = str(s).strip().split("/")
        return f"{a}-{m}-{d}"
    except (ValueError, AttributeError):
        return ""

def menu() -> None:
    gerenciador = Cadastro()
    historico_acoes = Pilha()

    while True:
        print("\n" + "="*50)
        print("          MENU PRINCIPAL - CORREIOS UNASP")
        print("="*50)
        print(" 1. Importar ficha de campo")
        print(" 2. Gerenciar Encomendas (Cadastrar, Alocar Prateleira, Editar, Remover)")
        print(" 3. Gerenciar Recursos / Inventário (Prateleiras do Setor)")
        print(" 4. Agenda de um dia (faixa de horário)")
        print(" 5. Consultar disponibilidade de um recurso")
        print(" 6. Lista de espera")
        print(" 7. Desfazer a última operação")
        print(" 8. Índice em disco do histórico")
        print(" 9. Relatório de desempenho das estruturas")
        print("10. Conflito de deslocamento")
        print("11. Gravar relatório em arquivo")
        print(" 0. Sair")
        print("-" * 50)

        selecao = input("Digite a opção desejada: ").strip()
        
        try:
            if selecao == "1":
                print("\n" + "="*50)
                print("      IMPORTAR FICHA DE CAMPO PARA A BASE")
                print("="*50)
                caminho = input(f"Digite o caminho do arquivo de origem (padrão: ficha.txt): ").strip()
                if not caminho:
                    caminho = "pedidos.csv"
                    
                registros = gerenciador.importar_ficha_campo(caminho)
                
                if not registros:
                    print(f"⚠️ Nenhum registro encontrado ou arquivo '{caminho}' não existe.")
                else:
                    print(f"\n[SUCESSO] Foram lidos {len(registros)} registros do arquivo '{caminho}'.")
                    for reg in registros:
                        print(reg)

            elif selecao == "2":
                print("\n--- GESTÃO DE ENCOMENDAS E ALOCAÇÃO ---")
                acao = input("Escolha a ação [cadastrar, editar, remover]: ").strip().lower()
                
                if acao == "cadastrar":
                    print("\n" + "="*50)
                    print("         CADASTRO DE NOVA ENCOMENDA")
                    print("="*50)
                    
                    while True:
                        # RE-LE O ARQUIVO EM DISCO A CADA TENTATIVA (garante dado atualizado)
                        pedidos_existentes = gerenciador.carregar_dados()
                        etiquetas_cadastradas = [
                            str(p.get("numEtiqueta", "")).strip().upper() 
                            for p in pedidos_existentes 
                            if str(p.get("numEtiqueta", "")).strip()
                        ]
                        
                        num_etiqueta = str(input("Número da Etiqueta: ")).strip().upper()
                        
                        if not num_etiqueta:
                            print("⚠️ A etiqueta não pode estar vazia.")
                        elif num_etiqueta in etiquetas_cadastradas:
                            print(f"❌ ERRO CRÍTICO: A etiqueta '{num_etiqueta}' já está cadastrada no sistema! Escolha outro número.")
                        else:
                            break # Só sai do while se a etiqueta for inédita!

                    num_cadastro = input("Número de Cadastro (RA/ID): ").strip()
                    nome_destinatario = input("Nome do Destinatário: ").strip()

                    while True:
                        print(f"\n📦 Opções Válidas de Embalagem: {', '.join(gerenciador.EMBALAGENS_VALIDAS)}")
                        embalagem = input("Digite a Embalagem: ").strip().upper()
                        if gerenciador.validar_embalagem(embalagem):
                            break
                        print("❌ Embalagem inválida! O sistema trava até digitar uma opção permitida.")

                    transportadora = input("\nTransportadora (ex: SHOPEE, CORREIOS): ").strip().upper()

                    while True:
                        print(f"\n👤 Categorias Permitidas: {', '.join(gerenciador.CATEGORIAS_VALIDAS)}")
                        categoria_publico = input("Digite a Categoria do Público: ").strip().upper()
                        if gerenciador.validar_categoria(categoria_publico):
                            break
                        print(f"❌ Categoria '{categoria_publico}' inválida! Escolha exatamente uma da lista oficial.")

                    # Data de chegada efetiva opcional (pode ficar em branco se o pacote ainda não chegou)
                    while True:
                        data_chegada_input = input("\nData de Chegada Efetiva (Pressione ENTER se ainda não chegou): ").strip()
                        if not data_chegada_input:
                            data_chegada = ""
                            break
                        elif gerenciador.validar_data_iso(data_chegada_input):
                            data_chegada = data_chegada_input
                            break
                        print("❌ Data inválida! Use o formato correto (ex: DD/MM/AAAA).")

                    # Data prevista de chegada
                    while True:
                        data_prevista = input("Data Prevista de Chegada (Opcional - DD/MM/AAAA): ").strip()
                        if not data_prevista or gerenciador.validar_data_iso(data_prevista):
                            break
                        print("❌ Data prevista inválida! Use o formato correto.")

                    observacoes = input("\nObservações: ").strip()
                    palavra_chave = input("Palavra-chave: ").strip()

                    novo_pedido = {
                        "numEtiqueta": num_etiqueta,
                        "numCadastro": num_cadastro,
                        "embalagem": embalagem,
                        "transportadora": transportadora,
                        "destinatario": {
                            "nome": nome_destinatario,
                            "categoriaPublico": categoria_publico
                        },
                        "status": "AGUARDANDO",
                        "dataChegada": data_chegada,
                        "retirada": {
                            "retiradoPor": "", "parentesco": "", "statusRetirada": "PENDENTE",
                            "autorizacaoEmail": "NAO", "dataRetirada": ""
                        },
                        "detalhamento": {
                            "observacoes": observacoes,
                            "dataPrevistaChegada": data_prevista,
                            "palavraChave": palavra_chave
                        }
                    }

                    erros = gerenciador.validar_reserva(novo_pedido)
                    if erros:
                        print("\n⚠️ Erros encontrados:")
                        for e in erros: print(f"   - {e}")
                        return   # ou continue pedindo
                    gerenciador.cadastrar("pedido", novo_pedido)
                    
                    gerenciador.cadastrar("pedido", novo_pedido)
                    print("\n✅ Encomenda cadastrada com sucesso em pedidos.csv!")

                    historico_acoes.empilhar({
                        "tipo": "pedido",
                        "acao": "cadastrar",
                        "identificador": novo_pedido["numEtiqueta"],
                        "dados_novos": novo_pedido,      # <<< novo
                        "descricao": f"Cadastrar pedido {novo_pedido['numEtiqueta']}"
                    })
                    
                    # Alocação na Prateleira com Listagem e Validação de Prioridade ativa
                    alocar = input("\nDeseja alocar este item em uma prateleira agora? (s/n): ").strip().lower()
                    if alocar == 's':
                        print("\n" + "-"*55)
                        print("       PRATELEIRAS DISPONÍVEIS NO INVENTÁRIO")
                        print("-" * 55)
                        
                        recursos = gerenciador._ler_json(gerenciador.recurso)
                        if not recursos:
                            print("⚠️ Nenhuma prateleira cadastrada em inventario.json.")
                        else:
                            for r in recursos:
                                codigo = r.get("codigoRecurso")
                                nome = r.get("nomeRecurso")
                                prioridade_prat = r.get("prioridade", 4)
                                capacidade = r.get("capacidade", 0)
                                itens = r.get("itemVinculado", [])
                                livres = capacidade - len(itens)
                                print(f"📍 [{codigo}] {nome} | Prioridade: Nível {prioridade_prat} | Vagas: {livres}/{capacidade}")
                            
                            print("-" * 55)
                            while True:
                                cod_prat = input("Digite o código da prateleira desejada (ou digite CANCELAR): ").strip().upper()
                                if cod_prat == "CANCELAR":
                                    print("Operação de alocação cancelada.")
                                    break
                                
                                sucesso_aloc, msg = gerenciador.inserir_item_na_prateleira(
                                    cod_prat,
                                    novo_pedido["numEtiqueta"],
                                    novo_pedido["destinatario"]["categoriaPublico"]
                                )
                                print(msg)
                                if sucesso_aloc:
                                    historico_acoes.empilhar({
                                        "tipo": "pedido",
                                        "acao": "alocar",
                                        "identificador": novo_pedido["numEtiqueta"],
                                        "prateleira": cod_prat,
                                        "descricao": f"Alocar {novo_pedido['numEtiqueta']} em {cod_prat}"
                                    })
                                    break

                elif acao == "remover":
                    etq = input("Digite a etiqueta do pedido para remover: ").strip().upper()
                    snap     = gerenciador.buscar_pedido(etq)
                    prat_old = gerenciador.prateleiras_do_item(etq)

                    sucesso = gerenciador.remover("pedido", etq)
                    if sucesso:
                        historico_acoes.empilhar({
                            "tipo": "pedido",
                            "acao": "remover",
                            "identificador": etq,
                            "dados_anteriores": snap,        # <<< para reinserir
                            "prateleiras_anteriores": prat_old,  # <<< para re-alocar
                            "descricao": f"Remover pedido {etq}"
                        })
                        print(f"✅ Pedido removido! ({len(prat_old)} prateleira(s) liberada(s))")
                    else:
                        print("❌ Pedido não encontrado.")

                elif acao == "editar":
                    print("\n" + "="*50)
                    print("         MENU DE EDIÇÃO DE ENCOMENDA")
                    print("="*50)
                    
                    etq = input("Digite a etiqueta do pedido que deseja editar: ").strip().upper()
                    pedidos = gerenciador.carregar_dados()
                    pedido_alvo = next((p for p in pedidos if p.get("numEtiqueta").upper() == etq), None)
                    
                    if not pedido_alvo:
                        print(f"❌ Pedido com a etiqueta '{etq}' não foi encontrado.")
                    else:
                        print(f"\n📦 Encomenda encontrada | Destinatário: {pedido_alvo.get('destinatario', {}).get('nome', 'N/A')}")
                        print(" Escolha o que deseja editar:")
                        print(" [1] Apenas o Status Geral (ENTREGUE / AGUARDANDO)")
                        print(" [2] Dados de Chegada e Observações")
                        print(" [3] Informações de Retirada (Retirado por, Status da Retirada, Autorização)")
                        print(" [4] Editar todos os dados da encomenda")
                        
                        sub_opcao = input("Opção desejada [1-4]: ").strip()
                        
                        if sub_opcao == "1":
                            while True:
                                print("\nStatus permitidos: [ENTREGUE, AGUARDANDO]")
                                novo_status = input("Digite o novo status: ").strip().upper()
                                if novo_status in ["ENTREGUE", "AGUARDANDO"]:
                                    break
                                print("❌ Status inválido! Digite exatamente ENTREGUE ou AGUARDANDO.")

                            snap_antes = gerenciador.buscar_pedido(etq)                       # <<< NOVO
                            sucesso = gerenciador.editar("pedido", etq, {"status": novo_status})
                            if sucesso:
                                historico_acoes.empilhar({                                    # <<< NOVO
                                    "tipo": "pedido",                                         # <<< NOVO
                                    "acao": "editar",                                         # <<< NOVO
                                    "identificador": etq,                                     # <<< NOVO
                                    "dados_anteriores": snap_antes,                           # <<< NOVO
                                    "descricao": f"Editar status de {etq}"                    # <<< NOVO
                                })                                                            # <<< NOVO
                                print(f"✅ Status do pedido '{etq}' atualizado para '{novo_status}'!")

                        elif sub_opcao == "2":
                            while True:
                                data_chegada = input("\nNova Data de Chegada Efetiva (DD/MM/AAAA): ").strip()
                                if not data_chegada or gerenciador.validar_data_iso(data_chegada):
                                    break
                                print("❌ Data inválida! Use o formato correto.")

                            obs = input("Novas Observações: ").strip()
                            palavra = input("Nova Palavra-chave: ").strip()

                            dados_chegada = {
                                "dataChegada": data_chegada,
                                "detalhamento": {
                                    "observacoes": obs,
                                    "palavraChave": palavra
                                }
                            }
                            snap_antes = gerenciador.buscar_pedido(etq)                       # <<< NOVO
                            sucesso = gerenciador.editar("pedido", etq, dados_chegada)
                            if sucesso:
                                historico_acoes.empilhar({                                    # <<< NOVO
                                    "tipo": "pedido",                                         # <<< NOVO
                                    "acao": "editar",                                         # <<< NOVO
                                    "identificador": etq,                                     # <<< NOVO
                                    "dados_anteriores": snap_antes,                           # <<< NOVO
                                    "descricao": f"Editar chegada de {etq}"                   # <<< NOVO
                                })                                                            # <<< NOVO
                                print(f"✅ Dados de chegada da encomenda '{etq}' atualizados!")

                        elif sub_opcao == "3":
                            retirado_por = input("\nRetirado por (Nome): ").strip()
                            parentesco = input("Parentesco / Vínculo (ex: Próprio, Amigo): ").strip()

                            while True:
                                print("Status de Retirada permitidos: [PENDENTE, CONCLUIDO]")
                                status_ret = input("Status da Retirada: ").strip().upper()
                                if status_ret in ["PENDENTE", "CONCLUIDO"]:
                                    break
                                print("❌ Opção inválida! Digite PENDENTE ou CONCLUIDO.")

                            while True:
                                print("Autorização por E-mail permitidas: [SIM, NAO]")
                                autorizacao = input("Autorização por E-mail: ").strip().upper()
                                if autorizacao in ["SIM", "NAO", "NÃO"]:
                                    autorizacao = "NAO" if autorizacao == "NÃO" else autorizacao
                                    break
                                print("❌ Opção inválida! Digite SIM ou NAO.")

                            while True:
                                data_ret = input("Data da Retirada (DD/MM/AAAA): ").strip()
                                if not data_ret or gerenciador.validar_data_iso(data_ret):
                                    break
                                print("❌ Data inválida!")

                            dados_retirada = {
                                "retirada": {
                                    "retiradoPor": retirado_por,
                                    "parentesco": parentesco,
                                    "statusRetirada": status_ret,
                                    "autorizacaoEmail": autorizacao,
                                    "dataRetirada": data_ret
                                }
                            }
                            snap_antes = gerenciador.buscar_pedido(etq)                       # <<< NOVO
                            sucesso = gerenciador.editar("pedido", etq, dados_retirada)
                            if sucesso:
                                historico_acoes.empilhar({                                    # <<< NOVO
                                    "tipo": "pedido",                                         # <<< NOVO
                                    "acao": "editar",                                         # <<< NOVO
                                    "identificador": etq,                                     # <<< NOVO
                                    "dados_anteriores": snap_antes,                           # <<< NOVO
                                    "descricao": f"Editar retirada de {etq}"                  # <<< NOVO
                                })                                                            # <<< NOVO
                                print(f"✅ Informações de retirada do pedido '{etq}' atualizadas!")

                                if status_ret == "CONCLUIDO":
                                    liberou = gerenciador.remover_item_da_prateleira(etq)
                                    if liberou:
                                        print(f"📦 Item '{etq}' removido da prateleira.")
                                    else:
                                        print(f"ℹ️ Item '{etq}' não estava em prateleira.")

                        elif sub_opcao == "4":
                            print("\n--- Edição Completa da Encomenda ---")
                            num_cad = input("Número de Cadastro (RA/ID): ").strip()
                            nome_dest = input("Nome do Destinatário: ").strip()
                            
                            while True:
                                print(f"📦 Embalagens Válidas: {', '.join(gerenciador.EMBALAGENS_VALIDAS)}")
                                embalagem = input("Embalagem: ").strip().upper()
                                if gerenciador.validar_embalagem(embalagem):
                                    break
                                print("❌ Embalagem inválida!")
                                
                            transp = input("Transportadora: ").strip().upper()
                            
                            while True:
                                print(f"👤 Categorias Permitidas: {', '.join(gerenciador.CATEGORIAS_VALIDAS)}")
                                cat_pub = input("Categoria do Público: ").strip().upper()
                                if gerenciador.validar_categoria(cat_pub):
                                    break
                                print("❌ Categoria inválida!")
                                
                            while True:
                                print("Status permitidos: [ENTREGUE, AGUARDANDO]")
                                status_input = input("Status Geral: ").strip().upper()
                                if status_input in ["ENTREGUE", "AGUARDANDO"]:
                                    break
                                print("❌ Status inválido!")

                            dados_completos = {
                                "numCadastro": num_cad,
                                "embalagem": embalagem,
                                "transportadora": transp,
                                "destinatario": {"nome": nome_dest, "categoriaPublico": cat_pub},
                                "status": status_input
                            }
                            snap_antes = gerenciador.buscar_pedido(etq)                       # <<< NOVO
                            sucesso = gerenciador.editar("pedido", etq, dados_completos)
                            if sucesso:
                                historico_acoes.empilhar({                                    # <<< NOVO
                                    "tipo": "pedido",                                         # <<< NOVO
                                    "acao": "editar",                                         # <<< NOVO
                                    "identificador": etq,                                     # <<< NOVO
                                    "dados_anteriores": snap_antes,                           # <<< NOVO
                                    "descricao": f"Edição completa de {etq}"                  # <<< NOVO
                                })                                                            # <<< NOVO
                                print(f"✅ Dados principais da encomenda '{etq}' atualizados!")
                                if status_input == "ENTREGUE":                                # opcional
                                    if gerenciador.remover_item_da_prateleira(etq):
                                        print(f"📦 Item '{etq}' liberado da prateleira (ENTREGUE).")

            elif selecao == "3":
                print("\n--- GESTÃO DE PRATELEIRAS DO INVENTÁRIO ---")
                acao = input("Escolha a ação [cadastrar, remover]: ").strip().lower()
                
                if acao == "cadastrar":
                    novo_recurso = {
                        "codigoRecurso": input("Código da Prateleira (ex: PRAT-A-02): ").strip(),
                        "nomeRecurso": input("Nome da Prateleira: ").strip(),
                        "tipoRecurso": "prateleira_estoque",
                        "capacidade": int(input("Capacidade máxima de itens: ") or 0),
                        "prioridade": int(input("Prioridade (1 a 4): ") or 4),
                        "local": "estoque_correios",
                        "observacoesRecurso": input("Observações: ").strip(),
                        "itemVinculado": []
                    }
                    recursos_existentes = gerenciador._ler_json(gerenciador.recurso)
                    erros = gerenciador.validar_recurso(novo_recurso, recursos_existentes)
                    
                    if erros:
                        print("\n⚠️ Erros encontrados:")
                        for e in erros: print(f"   - {e}")
                    else:
                        gerenciador.cadastrar("recurso", novo_recurso)
                        print("✅ Prateleira cadastrada!")
                        historico_acoes.empilhar({
                            "tipo": "recurso",
                            "acao": "cadastrar",
                            "identificador": novo_recurso["codigoRecurso"],
                            "dados_novos": novo_recurso,
                            "descricao": f"Cadastrar prateleira {novo_recurso['codigoRecurso']}"
                        })
                        
                elif acao == "remover":
                    cod = input("Digite o código da prateleira a remover: ").strip().upper()
                    snap = gerenciador.buscar_recurso(cod)

                    sucesso = gerenciador.remover("recurso", cod)
                    if sucesso:
                        historico_acoes.empilhar({
                            "tipo": "recurso",
                            "acao": "remover",
                            "identificador": cod,
                            "dados_anteriores": snap,
                            "descricao": f"Remover prateleira {cod}"
                        })
                        print("✅ Prateleira removida!")
                    else:
                        print("❌ Não encontrada.")

            elif selecao == "4":
                print("\n--- 4. AGENDA DE UM DIA (FAIXA DE HORÁRIO) ---")
                while True:
                    inicio_faixa = input("Data/Hora Inicial (ex: DD/MM/AAAA): ").strip()
                    if gerenciador.validar_data_iso(inicio_faixa):
                        data = inicio_faixa
                        break
                    print("❌ Data inválida! Use o formato correto (ex: DD/MM/AAAA).")
                while True:
                    fim_faixa = input("Data/Hora Final (ex: DD/MM/AAAA): ").strip()
                    if gerenciador.validar_data_iso(fim_faixa):
                        data = fim_faixa
                        break
                    print("❌ Data inválida! Use o formato correto (ex: DD/MM/AAAA).")
                
                pedidos = gerenciador.carregar_dados()
                contador_visitados = 0
                resultados = []

                for p in pedidos:
                    contador_visitados += 1
                    detalhamento = p.get("detalhamento", {})
                    data = detalhamento.get("dataPrevistaChegada", "").strip()
                    if data and inicio_faixa <= data <= fim_faixa:
                        resultados.append(p)

                print(f"\n[RESULTADO] Encontradas {len(resultados)} encomendas na faixa.")
                print(f"📊 MÉTRICA - Registros examinados/visitados: {contador_visitados}")

            elif selecao == "5":
                print("\n" + "="*50)
                print("       CONSULTA DE DISPONIBILIDADE DE RECURSOS")
                print("="*50)
                
                recursos = gerenciador._ler_json(gerenciador.recurso)
                if not recursos:
                    print("⚠️ Nenhum recurso cadastrado no inventário.")
                else:
                    for r in recursos:
                        codigo = r.get("codigoRecurso")
                        nome = r.get("nomeRecurso")
                        prioridade = r.get("prioridade", 4)
                        capacidade = r.get("capacidade", 0)
                        itens = r.get("itemVinculado", [])
                        ocupados = len(itens)
                        livres = capacidade - ocupados
                        
                        print(f"📦 Recurso: {codigo} - {nome} (Prioridade: Nível {prioridade})")
                        print(f"   • Capacidade Máxima: {capacidade} | Livres: {livres}")
                        print(f"   • Itens Alocados: {itens if itens else 'Nenhum'}")
                        print("-" * 40)

            elif selecao == "6":
                print("\n" + "="*50)
                print("   6. LISTA DE ESPERA POR PRATELEIRA")
                print("="*50)
                print("  Critério: encomendas ENTREGUE que NÃO estão em nenhuma prateleira.")
                print("  (AGUARDANDO não entra: ainda não chegaram fisicamente.)")

                pedidos  = gerenciador.carregar_dados()
                recursos = gerenciador._ler_json(gerenciador.recurso)

                # ---- itens já alocados em alguma prateleira ----
                alocados = set()
                for r in recursos:
                    for item in r.get("itemVinculado", []):
                        alocados.add(str(item).strip().upper())

                # ---- lista de espera = ENTREGUE e sem prateleira ----
                espera = [
                    p for p in pedidos
                    if p.get("status", "").strip().upper() == "ENTREGUE"
                    and str(p.get("numEtiqueta", "")).strip().upper() not in alocados
                ]

                if not espera:
                    print("\n✅ Nenhuma encomenda ENTREGUE aguardando prateleira.")
                else:
                    print(f"\n📦 {len(espera)} encomenda(s) na lista de espera.")

                    # ---- vagas por prateleira ----
                    print("\n--- Vagas disponíveis por prateleira ---")
                    for r in recursos:
                        cap   = r.get("capacidade", 0)
                        itens = r.get("itemVinculado", [])
                        print(f"  [{r.get('codigoRecurso')}] {r.get('nomeRecurso')} "
                            f"| P{r.get('prioridade', 4)} | vagas: {cap - len(itens)}/{cap}")

                    # ---- escolha da estrutura ----
                    print("\nEscolha a estrutura que decide a ORDEM de alocação:")
                    print(" [1] Fila FIFO  (ordem de chegada ao setor)")
                    print(" [2] Min-Heap   (maior prioridade primeiro)")
                    est = input("Opção: ").strip()

                    mapa = gerenciador.MAPA_PRIORIDADE_CATEGORIA
                    primeiros = []          # <<< guarda os 3 primeiros na ordem escolhida

                    if est == "1":
                        fila = Fila()
                        for p in espera:                    # FIFO usa a ordem do CSV
                            fila.enfileirar(p)
                        print("\n🔵 Ordem de alocação — Fila FIFO:")
                        ordem = 1
                        while not fila.vazia():
                            p   = fila.desenfileirar()
                            cat = p.get("destinatario", {}).get("categoriaPublico", "?")
                            pri = mapa.get(cat.strip().upper(), 4)
                            print(f"  {ordem:>2}º → P{pri} | {p['numEtiqueta']:<20} | {cat}")
                            if ordem <= 3:
                                primeiros.append(p)
                            ordem += 1
                        print(f"\n📊 Operações na Fila: {fila.operacoes}")

                    elif est == "2":
                        # normaliza dataChegada para ISO (bug do DD/MM/YYYY lexicográfico)
                        espera_iso = [
                            {**p, "dataChegada": _para_iso(p.get("dataChegada", ""))}
                            for p in espera
                        ]
                        h = MinHeap()
                        for p in espera_iso:
                            h.inserir(p)
                        print("\n🟢 Ordem de alocação — Min-Heap:")
                        ordem = 1
                        while not h.vazio():
                            p   = h.remover()
                            cat = p.get("destinatario", {}).get("categoriaPublico", "?")
                            pri = mapa.get(cat.strip().upper(), 4)
                            print(f"  {ordem:>2}º → P{pri} | {p['numEtiqueta']:<20} | {cat}")
                            if ordem <= 3:
                                primeiros.append(p)
                            ordem += 1
                        print(f"\n📊 Operações no Heap: {h.operacoes}")
                        if hasattr(h, "coerente"):
                            print(f"✅ coerente() = {h.coerente()}")
                        else:
                            print("⚠️ coerente() ainda NÃO implementado em Heap.py (checklist).")

                    else:
                        print("⚠️ Opção inválida — nenhuma estrutura escolhida.")

                    # ---- oferece alocar os 3 primeiros na ordem escolhida ----
                    if primeiros and input("\nDeseja alocar os 3 primeiros agora? (s/n): ").strip().lower() == "s":
                        cod = input("Código da prateleira de destino: ").strip().upper()
                        for p in primeiros:
                            ok, msg = gerenciador.inserir_item_na_prateleira(
                                cod,
                                p["numEtiqueta"],
                                p.get("destinatario", {}).get("categoriaPublico")
                            )
                            print(f"  {p['numEtiqueta']}: {msg}")
                            if not ok:
                                break

            elif selecao == "7":
                print("\n" + "="*50)
                print("           DESFAZER A ÚLTIMA OPERAÇÃO (PILHA)")
                print("="*50)

                if historico_acoes.vazia():
                    print("❌ Não há operações recentes para desfazer.")
                else:
                    # espiar antes de desempilhar
                    topo = historico_acoes.espiar()
                    print(f"🔄 Vai desfazer: {topo.get('descricao', topo)}")
                    if input("Confirma? (s/n): ").strip().lower() != "s":
                        print("Cancelado — a pilha não foi alterada.")
                    else:
                        acao_undo = historico_acoes.desempilhar()
                        tipo     = acao_undo.get("tipo")
                        acao     = acao_undo.get("acao")
                        id_alvo  = acao_undo.get("identificador")
                        ok       = False

                        try:
                            # ---------- cadastrar → desfazer é remover ----------
                            if acao == "cadastrar":
                                ok = gerenciador.remover(tipo, id_alvo)
                                if ok:
                                    print(f"✅ '{id_alvo}' ({tipo}) removido do sistema.")
                                else:
                                    print(f"❌ '{id_alvo}' não foi encontrado para remover.")

                            # ---------- remover → desfazer é reinserir ----------
                            elif acao == "remover":
                                dados = acao_undo.get("dados_anteriores")
                                if not dados:
                                    print("❌ Snapshot não guardado — impossível desfazer.")
                                else:
                                    if tipo == "pedido":
                                        try:
                                            gerenciador.cadastrar("pedido", dados)
                                            # re-alocar nas prateleiras onde estava
                                            for prat in acao_undo.get("prateleiras_anteriores", []):
                                                gerenciador.inserir_item_na_prateleira(
                                                    prat,
                                                    id_alvo,
                                                    dados.get("destinatario", {}).get("categoriaPublico")
                                                )
                                            ok = True
                                            print(f"✅ Pedido '{id_alvo}' reinserido"
                                                f" (prateleiras restauradas: "
                                                f"{len(acao_undo.get('prateleiras_anteriores', []))}).")
                                        except ValueError as e:
                                            print(f"❌ Reinserção falhou: {e}")
                                    elif tipo == "recurso":
                                        gerenciador.cadastrar("recurso", dados)
                                        ok = True
                                        print(f"✅ Prateleira '{id_alvo}' restaurada.")

                            # ---------- editar → desfazer é re-aplicar o snapshot antigo ----------
                            elif acao == "editar":
                                dados = acao_undo.get("dados_anteriores")
                                if not dados:
                                    print("❌ Snapshot não guardado — impossível desfazer.")
                                else:
                                    # remover campos que não existem no cadastro
                                    antigos = {k: v for k, v in dados.items()
                                            if k not in ("numEtiqueta",)}
                                    ok = gerenciador.editar(tipo, id_alvo, antigos)
                                    if ok:
                                        print(f"✅ Edição de '{id_alvo}' revertida.")

                            # ---------- alocar → desfazer é liberar a prateleira ----------
                            elif acao == "alocar":
                                prat = acao_undo.get("prateleira")
                                ok = gerenciador.remover_item_da_prateleira(id_alvo)
                                if ok:
                                    print(f"✅ Item '{id_alvo}' liberado da prateleira {prat}.")

                            else:
                                print(f"⚠️ Ação desconhecida '{acao}' — nada foi desfeito.")

                        except Exception as e:
                            print(f"❌ Erro ao desfazer: {e}. Reempilhando...")
                            historico_acoes.empilhar(acao_undo)   # devolve à pilha

                        print(f"📊 Operações restantes na pilha: {historico_acoes.tamanho()}")
                        
            elif selecao == "8":
                print("\n" + "="*55)
                print("   8. ÍNDICE EM DISCO DO HISTÓRICO (ÁRVORE B)")
                print("="*55)

                pedidos = gerenciador.carregar_dados()
                pares = []
                sem_data = 0
                for p in pedidos:
                    data = (p.get("dataChegada", "")
                            or p.get("detalhamento", {}).get("dataPrevistaChegada", ""))
                    chave = _data_para_chave(data)
                    if chave is None:
                        sem_data += 1
                        continue
                    pares.append((chave, p))

                if not pares:
                    print("⚠️ Nenhum pedido com data válida para indexar.")
                else:
                    print(f"📦 {len(pares)} pedido(s) indexável(is)"
                        f"  ({sem_data} ignorado(s) por falta de data)\n")

                    # ---- constrói três árvores B com ordens diferentes ----
                    resultados = []
                    for m in (3, 5, 51):
                        arv = B(m=m)                     # B = arvoreb.ArvoreB (já importado no topo)
                        for chave, ped in pares:
                            arv.inserir(chave, ped)
                        resultados.append({
                            "m": m,
                            "altura": arv.altura(),
                            "nos": arv.contar_nos(),
                            "divisoes": arv.divisoes,
                            "ocupacao": arv.ocupacao_media(),
                            "coerente": arv.coerente(),
                            "arvore": arv,
                            "chaves": arv.n_chaves,
                        })

                    # ---- tabela 1: construção ----
                    print(f"{'m':>3} | {'altura':>6} | {'nós':>4} | {'chaves':>6} | "
                        f"{'divisões':>8} | {'ocup.':>6} | {'coerente':>8}")
                    print("-" * 62)
                    for r in resultados:
                        print(f"{r['m']:>3} | {r['altura']:>6} | {r['nos']:>4} | "
                            f"{r['chaves']:>6} | {r['divisoes']:>8} | "
                            f"{r['ocupacao']:>5.1%} | {str(r['coerente']):>8}")

                    # ---- tabela 2: busca (amostras) ----
                    # min e max por varredura manual (sem sorted — §7.7)
                    chaves_ord = [c for c, _ in pares]
                    cmin = cmax = chaves_ord[0]
                    for c in chaves_ord:
                        if c < cmin: cmin = c
                        if c > cmax: cmax = c
                    amostras = [cmin, (cmin + cmax) // 2, cmax, 99999999]   # 4ª = inexistente
                    rotulos = ["1ª", "meio", "última", "inexist."]

                    print(f"\n--- Nós visitados por busca (cada nó = 1 bloco de disco) ---")
                    print(f"{'m':>3} | " + " | ".join(f"{r:>8}" for r in rotulos))
                    print("-" * 50)
                    for r in resultados:
                        visitas = [r["arvore"].buscar(c)[1] for c in amostras]
                        print(f"{r['m']:>3} | " + " | ".join(f"{v:>8}" for v in visitas))

                    # ---- custo acumulado de construção ----
                    print("\n--- Custo acumulado de construção do índice ---")
                    for r in resultados:
                        print(f"  m={r['m']:>2}: "
                            f"{r['arvore'].nos_visitados:>5} nós visitados, "
                            f"{r['divisoes']:>4} divisões")

                    # ---- coerência global ----
                    todos_ok = all(r["coerente"] for r in resultados)
                    print(f"\n{'✅' if todos_ok else '❌'} coerente() em todas as ordens: {todos_ok}")

                    # ---- lembrete do bloqueio da comparação com AVL ----
                    print("\nℹ️ Para o achado A3 completo (comparação com a AVL),")
                    print("   falta a BST/AVL em arvore.py (§7.2 do caderno).")
                    print("   Hoje arvore.py contém o mesmo código de arvoreb.py.")

            elif selecao == "9":
                print("\n" + "="*55)
                print("     RELATÓRIO DE DESEMPENHO DAS ESTRUTURAS")
                print("="*55)

                from relatorio import gerar_secoes

                secoes = gerar_secoes(gerenciador)
                for titulo, corpo in secoes:
                    print(f"\n--- {titulo} ---")
                    print(corpo)

                print("\nℹ️  Use a opção 11 para gravar este relatório em relatorio.txt.")

            elif selecao == "10":
                print("\n" + "="*55)
                print("   10. MENOR CAMINHO NO CAMPUS [EXTENSÃO B]")
                print("="*55)

                from trajetoria import (montar_grafo, menos_trechos,
                                        tempo_minimo, peso_do_caminho)

                grafo = montar_grafo("trechos.csv")
                if not grafo:
                    print("⚠️ 'trechos.csv' não encontrado ou vazio.")
                    print("   Colunas esperadas: origem;destino;segundos")
                else:
                    locais = list(grafo.keys())
                    n_arestas = sum(len(v) for v in grafo.values()) // 2
                    print(f"\n📍 Grafo do campus: {len(locais)} locais, {n_arestas} trechos.")
                    print("Locais disponíveis:")
                    for loc in locais:
                        print(f"   • {loc}")

                    origem  = input("\nOrigem : ").strip()
                    destino = input("Destino: ").strip()

                    if origem not in grafo or destino not in grafo:
                        print("❌ Um dos locais não existe no grafo.")
                    else:
                        t, cam_bfs, vis = menos_trechos(grafo, origem, destino)
                        s, cam_dij, rem, cmp = tempo_minimo(grafo, origem, destino)

                        if t is None and s is None:
                            print("\n❌ Não existe caminho entre esses locais.")
                        else:
                            # ---- resultado BFS ----
                            tempo_bfs = peso_do_caminho(grafo, cam_bfs)
                            print(f"\n🔵 BFS (menos trechos) — usando Fila")
                            print(f"   {t} trecho(s), {vis} nós visitados")
                            print(f"   Caminho: {' → '.join(cam_bfs)}")
                            print(f"   Tempo total desse caminho: {tempo_bfs}s")

                            # ---- resultado Dijkstra ----
                            print(f"\n🟢 Dijkstra (menor tempo) — usando Heap")
                            print(f"   {s}s, {rem} remoções do heap, {cmp} comparações")
                            print(f"   Caminho: {' → '.join(cam_dij)}")
                            print(f"   Trechos desse caminho: {len(cam_dij) - 1}")

                            # ---- análise: concordam ou divergem? ----
                            print("\n" + "-"*55)
                            if t == len(cam_dij) - 1:
                                print("✅ BFS e Dijkstra concordam no número de trechos.")
                                print("   A malha do setor não tem atalho que troque")
                                print("   'menos passos' por 'menos tempo'.")
                            else:
                                print("⚠️  AS RESPOSTAS DIVERGEM — é o achado do Anexo B:")
                                print(f"   • BFS respondeu '{t} trecho(s)' — pergunta:")
                                print("     'qual o caminho com menos passos?'")
                                print(f"   • Dijkstra respondeu '{len(cam_dij) - 1} trechos, {s}s' —")
                                print("     pergunta: 'qual o caminho mais rápido?'")
                                print(f"   As duas estão certas. O caminho do BFS leva "
                                    f"{tempo_bfs}s; o do Dijkstra, {s}s "
                                    f"(diferença: {tempo_bfs - s}s).")
                            print("-"*55)

                            # ---- contagem para o relatório ----
                            print(f"\n📊 Para o relatório:")
                            print(f"   BFS:      {vis} nós visitados, {t} trechos, {tempo_bfs}s")
                            print(f"   Dijkstra: {rem} remoções, {len(cam_dij) - 1} trechos, {s}s")

            elif selecao == "11":
                from relatorio import gerar_secoes, escrever_txt
                secoes = gerar_secoes(gerenciador)
                escrever_txt(secoes, "relatorio.txt")
                print(f"✅ 'relatorio.txt' gravado ({len(secoes)} seções).")

            elif selecao == "0":
                print("\nEncerrando programa... Até logo!")
                break
            else:
                print("\n❌ Opção inválida!")
                
        except ValueError as e:
            print(f"\n❌ Erro de formato nos dados inseridos: {e}. Tente novamente.")

if __name__ == "__main__":
    menu()