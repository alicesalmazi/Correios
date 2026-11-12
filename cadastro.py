import csv
import json
import os
from datetime import datetime


class Cadastro:
    def __init__(self, caminho="pedidos.csv", recurso="inventario.json"):
        self.caminho = caminho
        self.recurso = recurso

    # -------------------------------------------------------------------------
    # LISTAS OFICIAIS E MAPA DE PRIORIDADES
    # -------------------------------------------------------------------------
    TRANSPORTADORAS_VALIDAS = [
        "CORREIOS", "MERCADO LIVRE", "SHOPEE", "AMAZON", "ANJUN", "ALIEXPRESS", 
        "OBOTICÁRIO", "BRITÂNIA", "CPB", "ELETROLUX", "FERRO", "FM", "GFL", 
        "GROWTH", "UNILOG", "IMILE", "INSIDER", "JET", "LEVIS", "LOGAN", 
        "MAGALOG", "MAGALU", "MONDIAL", "NETSHOES", "PRIMEAIR", "PRIVALIA", 
        "RIACHUELO", "SHEIN", "SMART", "TIKTOK SHOP", "TOTAL", "TV", "VR", 
        "WEPINK", "YOUCOM", "JADLOG", "LOGGI", "ZARA", "RENNER", "TEMU", 
        "DANFE", "ULTRAFARMA", "C&A", "CACAU SHOW", "CENTAURO", "BRASPRESS", "JET MERCADO LIVRE"
    ]

    EMBALAGENS_VALIDAS = [
        "PACOTE", "PACOTE PEQUENO", "PACOTE GRANDE", 
        "CAIXA", "CAIXA PEQUENA", "CAIXA GRANDE", 
        "CARTA", "ENVELOPE", "VR"
    ]

    CATEGORIAS_VALIDAS = [
        "ALUNO INTERNO", "ALUNO EXTERNO", "EXTERNO",
        "FUNCIONÁRIO INTERNO", "FUNCIONÁRIO RESIDENTE", "FUNCIONÁRIO EXTERNO",
        "DEPARTAMENTOS", "CANTINA", "REITORIA", "JURÍDICO"
    ]

    MAPA_PRIORIDADE_CATEGORIA = {
        "DEPARTAMENTOS": 1,
        "CANTINA": 1,
        "REITORIA": 1,
        "JURÍDICO": 1,
        "ALUNO INTERNO": 2,
        "FUNCIONÁRIO INTERNO": 3,
        "FUNCIONÁRIO RESIDENTE": 3,
        "FUNCIONÁRIO EXTERNO": 3,
        "ALUNO EXTERNO": 4,
        "EXTERNO": 4
    }

    # -------------------------------------------------------------------------
    # MÉTODOS DE VALIDAÇÃO
    # -------------------------------------------------------------------------
    def validar_embalagem(self, embalagem):
        return embalagem.strip().upper() in self.EMBALAGENS_VALIDAS

    def validar_categoria(self, categoria):
        return categoria.strip().upper() in self.CATEGORIAS_VALIDAS

    def validar_data_iso(self, data_str):
        if data_str is None:
            return False
        data_clean = str(data_str).strip()
        if not data_clean:
            return False
        formatos = ["%d/%m/%YT%H:%M:%S", "%d/%m/%Y", "%d/%m/%Y %H:%M:%S"]
        for fmt in formatos:
            try:
                datetime.strptime(data_clean, fmt)
                return True
            except ValueError:
                continue
        return False

    def validar_recurso(self, recurso_dict, recursos_existentes=None):
        problemas = []
        codigo = recurso_dict.get("codigoRecurso")
        prioridade = recurso_dict.get("prioridade")
        capacidade = recurso_dict.get("capacidade")

        if recursos_existentes and any(r.get("codigoRecurso") == codigo for r in recursos_existentes):
            problemas.append("Código de recurso repetido.")

        try:
            if not (1 <= int(prioridade) <= 4):
                problemas.append("Prioridade fora da escala (1 a 4).")
        except (TypeError, ValueError):
            problemas.append("Prioridade inválida.")

        try:
            if int(capacidade) <= 0:
                problemas.append("Capacidade inválida ou menor/igual a zero.")
        except (TypeError, ValueError):
            problemas.append("Capacidade inválida.")

        return problemas

    # -------------------------------------------------------------------------
    # CARREGAMENTO E LEITURA DE DADOS (Com suporte a ponto e vírgula e utf-8-sig)
    # -------------------------------------------------------------------------
    def carregar_dados(self, caminho_csv=None):
        alvo = caminho_csv if caminho_csv is not None else self.caminho
        encomendas = []
        
        cabecalho_padrao = [
            "numEtiqueta", "numCadastro", "embalagem", "transportadora",
            "destinatario_nome", "destinatario_categoriaPublico", "status", "dataChegada",
            "retirada_retiradoPor", "retirada_parentesco", "retirada_statusRetirada",
            "retirada_autorizacaoEmail", "retirada_dataRetirada",
            "detalhamento_observacoes", "detalhamento_dataPrevistaChegada", "detalhamento_palavraChave"
        ]

        if not os.path.exists(alvo):
            with open(alvo, mode="w", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=cabecalho_padrao, delimiter=';')
                escritor.writeheader()
            return encomendas

        with open(alvo, mode="r", encoding="utf-8-sig") as arquivo:
            leitor = csv.DictReader(arquivo, delimiter=';')
            for linha in leitor:
                num_etq = linha.get("numEtiqueta", "")
                if not num_etq or not str(num_etq).strip():
                    continue

                encomenda = {
                    "numEtiqueta": (linha.get("numEtiqueta") or "").strip(),
                    "numCadastro": (linha.get("numCadastro") or "").strip(),
                    "embalagem":   (linha.get("embalagem") or "").strip(),
                    "transportadora": (linha.get("transportadora") or "").strip(),
                    "destinatario": {
                        "nome": (linha.get("destinatario_nome") or "").strip(),
                        "categoriaPublico": (linha.get("destinatario_categoriaPublico") or "").strip(),
                    },
                    "status": (linha.get("status") or "AGUARDANDO").strip(),
                    "dataChegada": (linha.get("dataChegada") or "").strip(),
                    "retirada": {
                        "retiradoPor": (linha.get("retirada_retiradoPor") or "").strip(),
                        "parentesco":  (linha.get("retirada_parentesco") or "").strip(),
                        "statusRetirada": (linha.get("retirada_statusRetirada") or "PENDENTE").strip(),
                        "autorizacaoEmail": (linha.get("retirada_autorizacaoEmail") or "NAO").strip(),
                        "dataRetirada": (linha.get("retirada_dataRetirada") or "").strip(),
                    },
                    "detalhamento": {
                        "observacoes": (linha.get("detalhamento_observacoes") or "").strip(),
                        "dataPrevistaChegada": (linha.get("detalhamento_dataPrevistaChegada") or "").strip(),
                        "palavraChave": (linha.get("detalhamento_palavraChave") or "").strip(),
                    },
                }
                encomendas.append(encomenda)
        return encomendas

    def _ler_json(self, caminho):
        if not os.path.exists(caminho):
            return []
        with open(caminho, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
                return dados if isinstance(dados, list) else [dados]
            except json.JSONDecodeError:
                return []

    def cadastrar(self, tipo, novo_item):
        if tipo == "recurso":
            dados = self._ler_json(self.recurso)
            dados.append(novo_item)
            with open(self.recurso, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=2, ensure_ascii=False)

        elif tipo == "pedido":
            etiqueta_nova = str(novo_item.get("numEtiqueta", "")).strip().upper()
            existentes = self.carregar_dados()
            if any(str(p.get("numEtiqueta", "")).strip().upper() == etiqueta_nova for p in existentes):
                raise ValueError(f"A etiqueta '{etiqueta_nova}' já existe no arquivo CSV!")

            cabecalho = [
                "numEtiqueta", "numCadastro", "embalagem", "transportadora",
                "destinatario_nome", "destinatario_categoriaPublico", "status", "dataChegada",
                "retirada_retiradoPor", "retirada_parentesco", "retirada_statusRetirada",
                "retirada_autorizacaoEmail", "retirada_dataRetirada",
                "detalhamento_observacoes", "detalhamento_dataPrevistaChegada", "detalhamento_palavraChave"
            ]

            linha_csv = {
                "numEtiqueta": novo_item.get("numEtiqueta", ""),
                "numCadastro": novo_item.get("numCadastro", ""),
                "embalagem": novo_item.get("embalagem", ""),
                "transportadora": novo_item.get("transportadora", ""),
                "destinatario_nome": novo_item.get("destinatario", {}).get("nome", ""),
                "destinatario_categoriaPublico": novo_item.get("destinatario", {}).get("categoriaPublico", ""),
                "status": novo_item.get("status", "AGUARDANDO"),
                "dataChegada": novo_item.get("dataChegada", ""),
                "retirada_retiradoPor": novo_item.get("retirada", {}).get("retiradoPor", ""),
                "retirada_parentesco": novo_item.get("retirada", {}).get("parentesco", ""),
                "retirada_statusRetirada": novo_item.get("retirada", {}).get("statusRetirada", "PENDENTE"),
                "retirada_autorizacaoEmail": novo_item.get("retirada", {}).get("autorizacaoEmail", "NAO"),
                "retirada_dataRetirada": novo_item.get("retirada", {}).get("dataRetirada", ""),
                "detalhamento_observacoes": novo_item.get("detalhamento", {}).get("observacoes", ""),
                "detalhamento_dataPrevistaChegada": novo_item.get("detalhamento", {}).get("dataPrevistaChegada", ""),
                "detalhamento_palavraChave": novo_item.get("detalhamento", {}).get("palavraChave", "")
            }

            arquivo_existe = os.path.exists(self.caminho) and os.path.getsize(self.caminho) > 0

            with open(self.caminho, mode="a", newline="", encoding="utf-8-sig") as arquivo:
                escritor = csv.DictWriter(arquivo, fieldnames=cabecalho, delimiter=';')
                if not arquivo_existe:
                    escritor.writeheader()
                escritor.writerow(linha_csv)

    # -------------------------------------------------------------------------
    # ALOCAÇÃO DE ITEM NA PRATELEIRA COM VALIDAÇÃO DE PRIORIDADE
    # -------------------------------------------------------------------------
    def inserir_item_na_prateleira(self, codigo_recurso, num_etiqueta, categoria_pedido=None):
        dados_inventario = self._ler_json(self.recurso)
        recurso_encontrado = None

        for rec in dados_inventario:
            if rec.get("codigoRecurso") == codigo_recurso:
                recurso_encontrado = rec
                break

        if not recurso_encontrado:
            return False, "❌ Recurso (prateleira) não encontrado no inventário."

        if categoria_pedido:
            prioridade_prateleira = int(recurso_encontrado.get("prioridade", 4))
            cat_limpa = categoria_pedido.strip().upper()
            prioridade_pedido = self.MAPA_PRIORIDADE_CATEGORIA.get(cat_limpa, 4)

            if prioridade_pedido > prioridade_prateleira:
                return False, (f"⚠️ Conflito de Prioridade! Esta prateleira é exclusiva para o nível {prioridade_prateleira} "
                             f"e você está tentando alocar um item de nível {prioridade_pedido} ({cat_limpa}).")

        capacidade_maxima = recurso_encontrado.get("capacidade", 0)
        itens_atuais = recurso_encontrado.get("itemVinculado", [])

        if len(itens_atuais) >= capacidade_maxima:
            return False, f"⚠️ Capacidade excedida! A prateleira {codigo_recurso} está lotada ({len(itens_atuais)}/{capacidade_maxima})."

        if num_etiqueta in itens_atuais:
            return False, "⚠️ Este item já está vinculado a esta prateleira."

        itens_atuais.append(num_etiqueta)
        recurso_encontrado["itemVinculado"] = itens_atuais

        with open(self.recurso, "w", encoding="utf-8") as f:
            json.dump(dados_inventario, f, indent=2, ensure_ascii=False)

        return True, f"✅ Item {num_etiqueta} alocado com sucesso na prateleira {codigo_recurso}!"

    def remover_item_da_prateleira(self, num_etiqueta):
        dados_inventario = self._ler_json(self.recurso)
        removido = False

        for rec in dados_inventario:
            itens = rec.get("itemVinculado", [])
            if num_etiqueta in itens:
                itens.remove(num_etiqueta)
                rec["itemVinculado"] = itens
                removido = True

        if removido:
            with open(self.recurso, "w", encoding="utf-8") as f:
                json.dump(dados_inventario, f, indent=2, ensure_ascii=False)

        return removido

    def buscar_pedido(self, etiqueta):
        alvo = str(etiqueta).strip().upper()
        for p in self.carregar_dados():
            if str(p.get("numEtiqueta", "")).strip().upper() == alvo:
                return p
        return None

    def buscar_recurso(self, codigo):
        alvo = str(codigo).strip().upper()
        for r in self._ler_json(self.recurso):
            if str(r.get("codigoRecurso", "")).strip().upper() == alvo:
                return r
        return None

    def prateleiras_do_item(self, num_etiqueta):
        alvo = str(num_etiqueta).strip().upper()
        return [
            r.get("codigoRecurso")
            for r in self._ler_json(self.recurso)
            if alvo in [str(x).strip().upper() for x in r.get("itemVinculado", [])]
        ]

    def validar_reserva(self, pedido):
        """Valida um pedido de encomenda (§7.5 adaptado ao domínio correios).
        Devolve lista de problemas."""
        problemas = []
        etq = str(pedido.get("numEtiqueta", "")).strip().upper()
        if not etq:
            problemas.append("Etiqueta vazia.")
        elif self.buscar_pedido(etq) is not None:
            problemas.append("Etiqueta repetida no cadastro.")
        # categoria válida
        cat = pedido.get("destinatario", {}).get("categoriaPublico", "")
        if not self.validar_categoria(cat):
            problemas.append(f"Categoria inválida: {cat}")
        # embalagem válida
        emb = pedido.get("embalagem", "")
        if not self.validar_embalagem(emb):
            problemas.append(f"Embalagem inválida: {emb}")
        # statusRetirada coerente
        ret = pedido.get("retirada", {})
        if ret.get("statusRetirada", "").upper() == "CONCLUIDO":
            if not ret.get("retiradoPor", "").strip():
                problemas.append("Retirada CONCLUIDO exige 'retiradoPor'.")
            if not ret.get("dataRetirada", "").strip():
                problemas.append("Retirada CONCLUIDO exige 'dataRetirada'.")
            elif not self.validar_data_iso(ret["dataRetirada"]):
                problemas.append("dataRetirada inválida.")
        # autorização de email
        aut = ret.get("autorizacaoEmail", "").strip().upper()
        if aut and aut not in ("SIM", "NAO"):
            problemas.append("autorizacaoEmail deve ser SIM ou NAO.")
        return problemas

    def editar(self, tipo, identificador, novos_dados):
        if tipo == "recurso":
            dados = self._ler_json(self.recurso)
            encontrado = False
            for item in dados:
                if item.get("codigoRecurso") == identificador:
                    item.update(novos_dados)
                    encontrado = True
                    break
            if encontrado:
                with open(self.recurso, "w", encoding="utf-8") as f:
                    json.dump(dados, f, indent=2, ensure_ascii=False)
            return encontrado

        elif tipo == "pedido":
            if not os.path.exists(self.caminho):
                return False
            
            linhas = []
            cabecalho = None
            encontrado = False

            with open(self.caminho, mode="r", encoding="utf-8-sig") as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=';')
                cabecalho = leitor.fieldnames
                
                novos_campos_csv = {}
                if "numCadastro" in novos_dados: novos_campos_csv["numCadastro"] = novos_dados["numCadastro"] or ""
                if "embalagem" in novos_dados: novos_campos_csv["embalagem"] = novos_dados["embalagem"] or ""
                if "transportadora" in novos_dados: novos_campos_csv["transportadora"] = novos_dados["transportadora"] or ""
                if "destinatario" in novos_dados:
                    dest = novos_dados["destinatario"] or ""
                    if "nome" in dest: novos_campos_csv["destinatario_nome"] = dest["nome"] or ""
                    if "categoriaPublico" in dest: novos_campos_csv["destinatario_categoriaPublico"] = dest["categoriaPublico"] or ""
                if "status" in novos_dados: novos_campos_csv["status"] = novos_dados["status"] or ""
                if "dataChegada" in novos_dados: novos_campos_csv["dataChegada"] = novos_dados["dataChegada"] or ""
                if "retirada" in novos_dados:
                    ret = novos_dados["retirada"] or ""
                    if "retiradoPor" in ret: novos_campos_csv["retirada_retiradoPor"] = ret["retiradoPor"] or ""
                    if "parentesco" in ret: novos_campos_csv["retirada_parentesco"] = ret["parentesco"] or ""
                    if "statusRetirada" in ret: novos_campos_csv["retirada_statusRetirada"] = ret["statusRetirada"] or ""
                    if "autorizacaoEmail" in ret: novos_campos_csv["retirada_autorizacaoEmail"] = ret["autorizacaoEmail"] or ""
                    if "dataRetirada" in ret: novos_campos_csv["retirada_dataRetirada"] = ret["dataRetirada"] or ""
                if "detalhamento" in novos_dados:
                    det = novos_dados["detalhamento"] or ""
                    if "observacoes" in det: novos_campos_csv["detalhamento_observacoes"] = det["observacoes"] or ""
                    if "dataPrevistaChegada" in det: novos_campos_csv["detalhamento_dataPrevistaChegada"] = det["dataPrevistaChegada"] or ""
                    if "palavraChave" in det: novos_campos_csv["detalhamento_palavraChave"] = det["palavraChave"] or ""

                for linha in leitor:
                    if linha.get("numEtiqueta") == identificador:
                        linha.update(novos_campos_csv)
                        encontrado = True
                    linhas.append(linha)

            if encontrado and cabecalho:
                with open(self.caminho, mode="w", newline="", encoding="utf-8-sig") as arquivo:
                    escritor = csv.DictWriter(arquivo, fieldnames=cabecalho, delimiter=';')
                    escritor.writeheader()
                    escritor.writerows(linhas)
            return encontrado
        return False

    def remover(self, tipo, identificador):
        if tipo == "recurso":
            dados = self._ler_json(self.recurso)
            novos_dados = [i for i in dados if i.get("codigoRecurso") != identificador]
            if len(novos_dados) < len(dados):
                with open(self.recurso, "w", encoding="utf-8") as f:
                    json.dump(novos_dados, f, indent=2, ensure_ascii=False)
                return True
            return False

        elif tipo == "pedido":
            if not os.path.exists(self.caminho):
                return False

            linhas = []
            cabecalho = None
            removido = False

            with open(self.caminho, mode="r", encoding="utf-8-sig") as arquivo:
                leitor = csv.DictReader(arquivo, delimiter=';')
                cabecalho = leitor.fieldnames
                for linha in leitor:
                    if linha.get("numEtiqueta") == identificador:
                        removido = True
                        continue
                    linhas.append(linha)

            if removido and cabecalho:
                with open(self.caminho, mode="w", newline="", encoding="utf-8-sig") as arquivo:
                    escritor = csv.DictWriter(arquivo, fieldnames=cabecalho, delimiter=';')
                    escritor.writeheader()
                    escritor.writerows(linhas)
                # >>> NOVO: limpa a prateleira junto <<<
                self.remover_item_da_prateleira(identificador)

            return removido
        return False

    def importar_ficha_campo(self, caminho):
        registros = []
        if not os.path.exists(caminho):
            return registros

        with open(caminho, "r", encoding="utf-8-sig") as f:
            cabecalho = None
            for linha in f:
                linha = linha.strip()
                if not linha or linha.startswith("#"):
                    continue
                partes = [p.strip() for p in linha.split(";")]
                if cabecalho is None:
                    cabecalho = partes
                else:
                    if len(partes) == len(cabecalho):
                        registros.append(dict(zip(cabecalho, partes)))
        return registros