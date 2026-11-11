"""
trajetoria.py — Trilha B: grafo do campus.
BFS com Fila (tads.py), Dijkstra com MinHeap (Heap.py).
"""
import csv
import os
from tads import Fila
from Heap import MinHeap


def montar_grafo(caminho="trechos.csv"):
    """
    Lê 'origem;destino;segundos'. Retorna {local: [(vizinho, seg), ...]}.
    Grafo NÃO-dirigido (insere as duas direções).
    """
    grafo = {}
    if not os.path.exists(caminho):
        return grafo
    with open(caminho, "r", encoding="utf-8-sig") as f:
        leitor = csv.DictReader(f, delimiter=";")
        for linha in leitor:
            o = (linha.get("origem") or "").strip()
            d = (linha.get("destino") or "").strip()
            try:
                s = int(linha.get("segundos", "0"))
            except (TypeError, ValueError):
                continue
            if not o or not d or s <= 0 or o == d:
                continue
            grafo.setdefault(o, []).append((d, s))
            grafo.setdefault(d, []).append((o, s))
    return grafo


def peso_do_caminho(grafo, caminho):
    """Soma os pesos das arestas do caminho. None se alguma aresta não existir."""
    if not caminho or len(caminho) < 2:
        return 0
    total = 0
    for i in range(len(caminho) - 1):
        a, b = caminho[i], caminho[i + 1]
        achou = None
        for viz, s in grafo.get(a, []):
            if viz == b:
                achou = s
                break
        if achou is None:
            return None
        total += achou
    return total


def menos_trechos(grafo, origem, destino):
    """BFS com Fila. Retorna (trechos, caminho, nos_visitados)."""
    if origem not in grafo or destino not in grafo:
        return (None, [], 0)
    fila = Fila()
    fila.enfileirar(origem)
    pai = {origem: None}
    visitados = 0
    while not fila.vazia():
        atual = fila.desenfileirar()
        visitados += 1
        if atual == destino:
            break
        for viz, _ in grafo.get(atual, []):
            if viz not in pai:
                pai[viz] = atual
                fila.enfileirar(viz)
    if destino not in pai:
        return (None, [], visitados)
    caminho = []
    cur = destino
    while cur is not None:
        caminho.append(cur)
        cur = pai[cur]
    caminho.reverse()
    return (len(caminho) - 1, caminho, visitados)


def tempo_minimo(grafo, origem, destino):
    """
    Dijkstra com MinHeap.
    Retorna (segundos, caminho, remocoes_do_heap, comparacoes_do_heap).
    """
    if origem not in grafo or destino not in grafo:
        return (None, [], 0, 0)

    h = MinHeap(chave=lambda it: (it[0], it[1]))   # desempata pelo nome
    h.inserir((0, origem))
    dist = {origem: 0}
    pai = {origem: None}
    visitado = set()
    remocoes = 0

    while not h.vazio():
        seg, no = h.remover()
        remocoes += 1
        if no in visitado:
            continue
        visitado.add(no)
        if no == destino:
            break
        for viz, peso in grafo.get(no, []):
            nd = seg + peso
            if viz not in dist or nd < dist[viz]:
                dist[viz] = nd
                pai[viz] = no
                h.inserir((nd, viz))

    if destino not in dist:
        return (None, [], remocoes, getattr(h, "comparacoes", 0))
    caminho = []
    cur = destino
    while cur is not None:
        caminho.append(cur)
        cur = pai.get(cur)
    caminho.reverse()
    return (dist[destino], caminho, remocoes, getattr(h, "comparacoes", 0))