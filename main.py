from cadastro import Cadastro
from tads import Fila, Pilha
from Heap import MinHeap
from arvore import ArvoreB

print("=== CENTRAL DE RESERVAS - Setor: Correios ===")

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
                    
                    gerenciador.cadastrar("pedido", novo_pedido)
                    print("\n✅ Encomenda cadastrada com sucesso em pedidos.csv!")
                    
                    historico_acoes.empilhar({
                        "tipo": "pedido",
                        "acao": "cadastrar",
                        "identificador": novo_pedido["numEtiqueta"]
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
                                    break

                elif acao == "remover":
                    etq = input("Digite o número da etiqueta do pedido para remover/excluir: ").strip().upper()
                    sucesso = gerenciador.remover("pedido", etq)
                    print("✅ Pedido removido com sucesso!" if sucesso else "❌ Pedido não encontrado.")

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
                            
                            sucesso = gerenciador.editar("pedido", etq, {"status": novo_status})
                            if sucesso:
                                print(f"✅ Status do pedido '{etq}' atualizado para '{novo_status}' com sucesso!")

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
                            sucesso = gerenciador.editar("pedido", etq, dados_chegada)
                            if sucesso:
                                print(f"✅ Dados de chegada da encomenda '{etq}' atualizados com sucesso!")

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
                            sucesso = gerenciador.editar("pedido", etq, dados_retirada)
                            if sucesso:
                                print(f"✅ Informações de retirada do pedido '{etq}' atualizadas com sucesso!")

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
                                "destinatario": {
                                    "nome": nome_dest,
                                    "categoriaPublico": cat_pub
                                },
                                "status": status_input
                            }
                            sucesso = gerenciador.editar("pedido", etq, dados_completos)
                            if sucesso:
                                print(f"✅ Dados principais da encomenda '{etq}' atualizados com sucesso!")

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
                        print("\n✅ Prateleira cadastrada com sucesso em inventario.json!")
                        
                elif acao == "remover":
                    cod = input("Digite o código da prateleira a remover: ").strip().upper()
                    sucesso = gerenciador.remover("recurso", cod)
                    print("✅ Prateleira removida!" if sucesso else "❌ Não encontrada.")

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
                    data = p.get("dataPrevistaChegada", "")
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
                print("\n--- 6. LISTA DE ESPERA E ATENDIMENTO ---")
                print("Escolha a estrutura de atendimento:")
                print(" [1] Fila FIFO (tads.py)")
                print(" [2] Heap de Prioridade (Heap.py)")
                est = input("Opção: ").strip()
                
                pedidos = gerenciador.carregar_dados()
                
                if est == "1":
                    from tads import Fila
                    fila = Fila()
                    for p in pedidos:
                        fila.enfileirar(p)
                    print(f"\n📊 MÉTRICA - Total de operações na Fila FIFO: {fila.operacoes}")
                elif est == "2":
                    from Heap import MinHeap
                    min_heap = MinHeap()
                    for p in pedidos:
                        min_heap.inserir(p)
                    print(f"\n📊 MÉTRICA - Total de operações no Min-Heap: {min_heap.operacoes}")

            elif selecao == "7":
                print("\n" + "="*50)
                print("           DESFAZER A ÚLTIMA OPERAÇÃO (PILHA)")
                print("="*50)
                
                if historico_acoes.vazia():
                    print("❌ Não há operações recentes para desfazer na Pilha.")
                else:
                    ultima_acao = historico_acoes.desempilhar()
                    tipo = ultima_acao.get("tipo")
                    acao = ultima_acao.get("acao")
                    id_alvo = ultima_acao.get("identificador")
                    
                    print(f"🔄 Desfazendo última ação registrada: {acao.upper()} de {tipo} ({id_alvo})...")
                    
                    if acao == "cadastrar":
                        sucesso = gerenciador.remover(tipo, id_alvo)
                        if sucesso:
                            print(f"✅ Operação desfeita com sucesso! O item '{id_alvo}' foi removido.")
                        else:
                            print(f"❌ Erro: O item '{id_alvo}' não foi encontrado para remoção.")
                        
                    print(f"📊 Operações restantes na pilha de histórico: {historico_acoes.tamanho()}")
                        
            elif selecao == "8":
                print("\n--- 8. ÍNDICE EM DISCO DO HISTÓRICO (ÁRVORE B) ---")
                m_ordem = int(input("Informe a ordem m da Árvore B (m >= 3): ") or 3)
                
                from arvore import ArvoreB
                arvore_b = ArvoreB(m=m_ordem)
                
                pedidos = gerenciador.carregar_dados()
                for p in pedidos:
                    chave = p.get("dataChegada", "") or p.get("detalhamento", {}).get("dataPrevistaChegada", "")
                    if chave:
                        arvore_b.inserir(chave, p)

                print("\n--- ESTATÍSTICAS DA ÁRVORE B ---")
                print(f"📊 Nós visitados acumulados: {arvore_b.nos_visitados}")
                print(f"📊 Divisões de nós realizadas: {arvore_b.divisoes}")
                print(f"📊 Altura da árvore: {arvore_b.altura()}")
                print(f"📊 Ocupação média: {arvore_b.ocupacao_media():.2f}")
                print(f"✅ Estrutura coerente? {arvore_b.coerente()}")

            elif selecao == "9":
                print("\n" + "="*50)
                print("       RELATÓRIO DE DESEMPENHO DAS ESTRUTURAS")
                print("="*50)
                
                pedidos = gerenciador.carregar_dados()
                print(f"📊 Total de registros carregados na base: {len(pedidos)}")
                
                from Heap import MinHeap
                h = MinHeap()
                for p in pedidos:
                    h.inserir(p)
                
                print(f"📈 Total de operações de reorganização (Heap): {h.operacoes}")
                print("✅ Status das estruturas: Operacionais e integradas.")

            elif selecao == "10":
                print("\n" + "="*50)
                print("       VERIFICAÇÃO DE CONFLITO DE DESLOCAMENTO")
                print("="*50)
                
                recursos = gerenciador._ler_json(gerenciador.recurso)
                conflitos_encontrados = False
                
                for r in recursos:
                    codigo = r.get("codigoRecurso")
                    capacidade = r.get("capacidade", 0)
                    itens = r.get("itemVinculado", [])
                    
                    if len(itens) > capacidade:
                        conflitos_encontrados = True
                        print(f"⚠️ Conflito crítico na Prateleira {codigo}: Excede a capacidade ({len(itens)}/{capacidade}).")
                
                if not conflitos_encontrados:
                    print("✅ Nenhum conflito de capacidade ou deslocamento detectado nas prateleiras.")

            elif selecao == "11":
                print("\n" + "="*50)
                print("       GRAVAÇÃO DE RELATÓRIO EM ARQUIVO")
                print("="*50)
                
                nome_relatorio = "relatorio_desempenho.txt"
                pedidos = gerenciador.carregar_dados()
                recursos = gerenciador._ler_json(gerenciador.recurso)
                
                with open(nome_relatorio, "w", encoding="utf-8") as f:
                    f.write("=== RELATÓRIO DE DESEMPENHO - SETOR CORREIOS UNASP ===\n")
                    f.write(f"Total de encomendas cadastradas: {len(pedidos)}\n")
                    f.write(f"Total de prateleiras no inventário: {len(recursos)}\n\n")
                    f.write("Status do sistema: Operacional\n")
                
                print(f"✅ Relatório gravado com sucesso no arquivo '{nome_relatorio}'!")

            elif selecao == "0":
                print("\nEncerrando programa... Até logo!")
                break
            else:
                print("\n❌ Opção inválida!")
                
        except ValueError as e:
            print(f"\n❌ Erro de formato nos dados inseridos: {e}. Tente novamente.")

if __name__ == "__main__":
    menu()