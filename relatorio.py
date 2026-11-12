"""
relatorio.py — Medições e gravação do relatório de desempenho.
Produz os números que alimentam A1, A2, A3, A4 (§10 do caderno).
Não usa sorted(), heapq, bisect, list.pop(0).
"""
from arvore import Arvore
from arvoreb import ArvoreB
import heap
from heap import MinHeap, heapsort


# ---------- utilidades ----------
def data_para_chave(s):
    """'DD/MM/YYYY' → inteiro YYYYMMDD ordenável. None se inválida."""
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


def extrair_pares(pedidos):
    """Lista [(chave_int, pedido)] cronológica + quantos sem data."""
    pares, sem = [], 0
    for p in pedidos:
        bruto = (p.get("dataChegada", "")
                 or p.get("detalhamento", {}).get("dataPrevistaChegada", ""))
        c = data_para_chave(bruto)
        if c is None:
            sem += 1
        else:
            pares.append((c, p))
    return pares, sem

def _chave_etiqueta(pedido):
    """Extrai o número final da etiqueta como inteiro ordenável.
    'ETQ-2026-79720' → 79720."""
    etq = str(pedido.get("numEtiqueta", "")).strip().upper()
    if "-" in etq:
        partes = etq.split("-")
        try:
            return int(partes[-1])
        except (ValueError, IndexError):
            return 0
    try:
        return int(etq)
    except ValueError:
        return 0


def extrair_pares_por_etiqueta(pedidos):
    """Pares (chave_etiqueta, pedido) ORDENADOS por chave (insertion sort).
    Simula o cenário do §10: base que 'volta do disco em ordem',
    fazendo a BST degenerar."""
    pares = [(_chave_etiqueta(p), p) for p in pedidos]

    # insertion sort manual (sem sorted — §7.7)
    for i in range(1, len(pares)):
        atual = pares[i]
        j = i - 1
        while j >= 0 and pares[j][0] > atual[0]:
            pares[j + 1] = pares[j]
            j -= 1
        pares[j + 1] = atual

    return pares

def _chaves_amostra(pares):
    """min, meio, max por varredura manual (sem sorted — §7.7)."""
    if not pares:
        return []
    cs = [c for c, _ in pares]
    mn = mx = cs[0]
    for c in cs:
        if c < mn: mn = c
        if c > mx: mx = c
    return [mn, (mn + mx) // 2, mx, 99999999]   # 4ª = inexistente


# ---------- A1: BST vs AVL ----------
def medir_bst_avl(pares):
    """Retorna dict pronto para tabela do A1."""
    if not pares:
        return {}

    amostras = _chaves_amostra(pares)
    resultado = {}

    for rotulo, balanceada in (("BST", False), ("AVL", True)):
        arv = Arvore(balanceada=balanceada)
        rot = 0

        # --- fase 1: inserção ---
        for c, p in pares:
            antes = getattr(arv, "rotacoes", 0)
            arv.inserir(c, p)
            rot += getattr(arv, "rotacoes", 0) - antes

        # captura ANTES de qualquer busca — §10 (A1) quer só inserção
        comp_ins = getattr(arv, "comparacoes", 0)

        # --- fase 2: buscas (não contaminam comp_ins) ---
        buscas = [arv.buscar(c)[1] for c in amostras]

        resultado[rotulo] = {
            "altura": arv.altura(),
            "comparacoes_insercao": comp_ins,
            "rotacoes": rot,
            "caminho_medio": arv.caminho_medio() if hasattr(arv, "caminho_medio") else "n/d",
            "busca_1a": buscas[0] if buscas else "-",
            "busca_meio": buscas[1] if buscas else "-",
            "busca_ultima": buscas[2] if buscas else "-",
            "busca_inexistente": buscas[3] if buscas else "-",
            "coerente": arv.coerente(),
        }

    return resultado


# ---------- A2: faixa × varredura ----------
def _faixas_por_quartis(pares):
    """
    4 quartis por VOLUME de pedidos (cada grupo tem n/4 pedidos)
    + 1 faixa extra com o dia de maior frequência.
    Sem sorted() — insertion sort manual (§7.7).
    """
    if not pares:
        return []

    chaves = [c for c, _ in pares]

    # insertion sort manual
    for i in range(1, len(chaves)):
        atual = chaves[i]
        j = i - 1
        while j >= 0 and chaves[j] > atual:
            chaves[j + 1] = chaves[j]
            j -= 1
        chaves[j + 1] = atual

    n = len(chaves)
    faixas = []
    for k in range(4):
        ini_idx = (k * n) // 4
        fim_idx = ((k + 1) * n) // 4 - 1
        if fim_idx >= ini_idx:
            faixas.append((chaves[ini_idx], chaves[fim_idx]))

    # dia de pico por contagem (dict só para cadastro/contagem — §15 permite)
    freq = {}
    for c in chaves:
        freq[c] = freq.get(c, 0) + 1
    pico = None
    maior = -1
    for c, q in freq.items():
        if q > maior:
            maior = q
            pico = c
    if pico is not None and (pico, pico) not in faixas:
        faixas.append((pico, pico))

    return faixas


def medir_faixas(pares, faixas):
    """
    faixas: lista de (inicio, fim). Para cada faixa devolve
    { 'BST': (qtd, nos), 'AVL': (qtd, nos), 'varredura': (qtd, registros) }
    """
    if not pares or not faixas:
        return []
    bst = Arvore(balanceada=False)
    avl = Arvore(balanceada=True)
    for c, p in pares:
        bst.inserir(c, p)
        avl.inserir(c, p)
    linhas = []
    for ini, fim in faixas:
        rb, nb = bst.faixa(ini, fim)
        ra, na = avl.faixa(ini, fim)
        # varredura manual
        vq, vv = [], 0
        for c, p in pares:
            vv += 1
            if ini <= c <= fim:
                vq.append(p)
        linhas.append({
            "faixa": (ini, fim),
            "BST": (len(rb), nb),
            "AVL": (len(ra), na),
            "varredura": (len(vq), vv),
        })
    return linhas


# ---------- A3: Árvore B ----------
def medir_btree(pares, ordens=(3, 5, 51)):
    """Retorna lista de dicts (um por ordem m)."""
    if not pares:
        return []
    saida = []
    for m in ordens:
        arv = ArvoreB(m=m)
        for c, p in pares:
            arv.inserir(c, p)
        saida.append({
            "m": m,
            "altura": arv.altura(),
            "nos": arv.contar_nos(),
            "chaves": arv.n_chaves,
            "divisoes": arv.divisoes,
            "ocupacao": arv.ocupacao_media(),
            "coerente": arv.coerente(),
            "arvore": arv,
        })
    return saida


# ---------- A4: Heap ----------
def medir_heap(pedidos, ks=(1, 5, 10, 20)):
    pedidos_iso = [
        {**p, "dataChegada": _para_iso(p.get("dataChegada", ""))}
        for p in pedidos
    ]
    h = MinHeap()
    for p in pedidos_iso:
        h.inserir(p)
    construcao = {
        "operacoes": getattr(h, "operacoes", 0),
        "comparacoes": getattr(h, "comparacoes", "n/d"),
        "trocas": getattr(h, "trocas", "n/d"),
        "coerente": h.coerente() if hasattr(h, "coerente") else "n/d",
    }
    ordenadas = heapsort(pedidos_iso)

    k_menores = getattr(heap, "k_menores_com_heap", None)
    topo = None
    if k_menores is not None:
        topo = {k: len(k_menores(pedidos_iso, k)) for k in ks}

    return {"construcao": construcao, "ordenadas": len(ordenadas), "top": topo}


# ---------- gerador central ----------
def gerar_secoes(gerenciador):
    """Retorna [(titulo, texto)] pronto para imprimir e/ou gravar."""
    pedidos = gerenciador.carregar_dados()
    pares, sem_data = extrair_pares(pedidos)
    secoes = []

    secoes.append((
        "BASE",
        f"Pedidos: {len(pedidos)}\n"
        f"Com data indexável: {len(pares)}\n"
        f"Sem data (ignorados): {sem_data}"
    ))

    # --- A1: BST vs AVL ---
    try:
        pares_etq = extrair_pares_por_etiqueta(pedidos)
        r = medir_bst_avl(pares_etq)
        linhas = []
        for rot in ("BST", "AVL"):
            d = r.get(rot, {})
            linhas.append(
                f"{rot:>3} | altura={d.get('altura'):>4} | "
                f"comp_ins={d.get('comparacoes_insercao'):>6} | "
                f"rot={d.get('rotacoes'):>4} | "
                f"caminho={d.get('caminho_medio')} | "
                f"busca(1ª/meio/últ/inex)={d.get('busca_1a')}/"
                f"{d.get('busca_meio')}/{d.get('busca_ultima')}/"
                f"{d.get('busca_inexistente')} | "
                f"coerente={d.get('coerente')}"
            )
        secoes.append(("A1 — BST vs AVL", "\n".join(linhas)))
    except Exception as e:
        secoes.append(("A1 — BST vs AVL", f"BLOQUEADO: {e}\n"
                       "→ corrija arvore.py (§7.2 do caderno)"))

    # --- A2: faixa × varredura (quartis por pedidos — sem sorted) ---
    try:
        faixas = _faixas_por_quartis(pares)
        r = medir_faixas(pares, faixas)
        linhas = []
        for d in r:
            ini, fim = d["faixa"]
            linhas.append(
                f"faixa=({ini},{fim}) | "
                f"BST: {d['BST'][0]} resg / {d['BST'][1]} nós | "
                f"AVL: {d['AVL'][0]} resg / {d['AVL'][1]} nós | "
                f"varredura: {d['varredura'][0]} resg / {d['varredura'][1]} examinados"
            )
        secoes.append(("A2 — Faixa × varredura", "\n".join(linhas)))
    except Exception as e:
        secoes.append(("A2 — Faixa × varredura", f"ERRO: {e}"))

    # --- A3: Árvore B ---
    try:
        r = medir_btree(pares)
        linhas = []
        for d in r:
            linhas.append(
                f"m={d['m']:>2} | altura={d['altura']:>3} | "
                f"nós={d['nos']:>4} | chaves={d['chaves']:>4} | "
                f"divisões={d['divisoes']:>4} | "
                f"ocup={d['ocupacao']:>5.1%} | coerente={d['coerente']}"
            )
        secoes.append(("A3 — Árvore B", "\n".join(linhas)))
    except Exception as e:
        secoes.append(("A3 — Árvore B", f"ERRO: {e}"))

    # --- A4: Heap ---
    r = medir_heap(pedidos)
    c = r["construcao"]
    linhas = [
        f"Construção do Min-Heap: operações={c['operacoes']} "
        f"comparações={c['comparacoes']} trocas={c['trocas']} "
        f"coerente={c['coerente']}",
        f"Heapsort: {r['ordenadas']} itens ordenados",
    ]
    if r["top"]:
        for k, v in r["top"].items():
            linhas.append(f"  k={k}: {v} extraídos com heap")
    else:
        linhas.append("  ⚠️ k_menores_com_heap ausente em heap.py (A4)")
    secoes.append(("A4 — Heap e Heapsort", "\n".join(linhas)))

    return secoes


def escrever_txt(secoes, caminho="relatorio.txt"):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=== RELATÓRIO DE DESEMPENHO — CENTRAL DE RESERVAS ===\n\n")
        for titulo, corpo in secoes:
            f.write(titulo + "\n")
            f.write("-" * len(titulo) + "\n")
            f.write(corpo + "\n\n")