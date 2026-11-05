"""
head.py
Heap e Heapsort aplicados ao sistema de encomendas do UNASP.

Nao utiliza heapq, sorted(), sort() ou bibliotecas de ordenacao.
A estrutura Heap e os algoritmos de insercao, remocao e Heapsort
foram implementados manualmente.

Formato esperado dos dados: o mesmo utilizado em encomenda.json.
"""

import json


# Prioridades definidas no README do projeto.
PRIORIDADES = {
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


def prioridade_da_encomenda(encomenda):
    """Identifica a prioridade usando destinatario.categoriaPublico."""
    destinatario = encomenda.get("destinatario", {})
    categoria = destinatario.get("categoriaPublico", "").strip().upper()
    return PRIORIDADES.get(categoria, 4)


def chave_da_encomenda(encomenda):
    """
    Define a ordem de atendimento:
    1) menor numero de prioridade;
    2) dataChegada mais antiga;
    3) numEtiqueta em ordem crescente.
    As datas ISO do arquivo JSON podem ser comparadas como texto.
    """
    data = encomenda.get("dataChegada") or "9999-12-31T23:59:59"
    etiqueta = str(encomenda.get("numEtiqueta", ""))
    return (prioridade_da_encomenda(encomenda), data, etiqueta)


class MinHeap:
    """Heap minimo: a encomenda de maior prioridade fica na raiz."""

    def __init__(self):
        self.elementos = []
        self.operacoes = 0

    def vazio(self):
        return len(self.elementos) == 0

    def tamanho(self):
        return len(self.elementos)

    def inserir(self, encomenda):
        """Insere uma encomenda e reorganiza o Heap de baixo para cima."""
        self.elementos.append(encomenda)
        indice = len(self.elementos) - 1
        self.operacoes += 1

        while indice > 0:
            pai = (indice - 1) // 2

            if chave_da_encomenda(self.elementos[indice]) < chave_da_encomenda(self.elementos[pai]):
                self.elementos[indice], self.elementos[pai] = (
                    self.elementos[pai], self.elementos[indice]
                )
                indice = pai
                self.operacoes += 1
            else:
                break

    def remover(self):
        """Remove e retorna a encomenda de maior prioridade."""
        if self.vazio():
            return None

        if len(self.elementos) == 1:
            self.operacoes += 1
            return self.elementos.pop()

        primeira = self.elementos[0]
        self.elementos[0] = self.elementos.pop()
        self.operacoes += 1
        self._descer(0)
        return primeira

    def _descer(self, indice):
        """Restaura a propriedade de Min-Heap a partir de um indice."""
        tamanho = len(self.elementos)

        while True:
            menor = indice
            esquerdo = 2 * indice + 1
            direito = 2 * indice + 2

            if (esquerdo < tamanho and
                    chave_da_encomenda(self.elementos[esquerdo]) <
                    chave_da_encomenda(self.elementos[menor])):
                menor = esquerdo

            if (direito < tamanho and
                    chave_da_encomenda(self.elementos[direito]) <
                    chave_da_encomenda(self.elementos[menor])):
                menor = direito

            if menor == indice:
                break

            self.elementos[indice], self.elementos[menor] = (
                self.elementos[menor], self.elementos[indice]
            )
            indice = menor
            self.operacoes += 1


def heapsort(encomendas):
    """
    Ordena uma lista de encomendas sem alterar a lista original.
    Retorna prioridade 1 antes de 2, 3 e 4.
    O algoritmo utiliza Max-Heap para produzir a ordem crescente.
    """
    lista = encomendas.copy()
    tamanho = len(lista)

    def descer_maximo(raiz, limite):
        maior = raiz
        esquerdo = 2 * raiz + 1
        direito = 2 * raiz + 2

        if (esquerdo < limite and
                chave_da_encomenda(lista[esquerdo]) >
                chave_da_encomenda(lista[maior])):
            maior = esquerdo

        if (direito < limite and
                chave_da_encomenda(lista[direito]) >
                chave_da_encomenda(lista[maior])):
            maior = direito

        if maior != raiz:
            lista[raiz], lista[maior] = lista[maior], lista[raiz]
            descer_maximo(maior, limite)

    # Etapa 1: construir o Max-Heap.
    indice = tamanho // 2 - 1
    while indice >= 0:
        descer_maximo(indice, tamanho)
        indice -= 1

    # Etapa 2: levar a maior chave para o final a cada iteracao.
    fim = tamanho - 1
    while fim > 0:
        lista[0], lista[fim] = lista[fim], lista[0]
        descer_maximo(0, fim)
        fim -= 1

    return lista


def carregar_encomendas(caminho="encomenda.json"):
    """
    Le os dados do arquivo JSON do projeto.
    Aceita tanto um unico objeto JSON quanto uma lista de encomendas.
    O modulo json e usado somente para ler o arquivo; Heap e Heapsort
    continuam implementados manualmente neste codigo.
    """
    arquivo = open(caminho, "r", encoding="utf-8")
    dados = json.load(arquivo)
    arquivo.close()

    if isinstance(dados, list):
        return dados
    return [dados]


def mostrar_encomendas(encomendas, titulo):
    print("\n" + titulo)
    if len(encomendas) == 0:
        print("Nenhuma encomenda cadastrada.")
        return

    for encomenda in encomendas:
        destinatario = encomenda.get("destinatario", {})
        print(
            "Prioridade:", prioridade_da_encomenda(encomenda),
            "| Etiqueta:", encomenda.get("numEtiqueta", "Sem etiqueta"),
            "| Destinatario:", destinatario.get("nome", "Nao informado"),
            "| Categoria:", destinatario.get("categoriaPublico", "Nao informada"),
            "| Data:", encomenda.get("dataChegada", "Nao informada")
        )


if __name__ == "__main__":
    # Carrega o arquivo encomenda.json que ja existe no projeto.
    encomendas = carregar_encomendas()

    # Demonstra o Heapsort.
    ordenadas = heapsort(encomendas)
    mostrar_encomendas(ordenadas, "ENCOMENDAS ORDENADAS COM HEAPSORT")

    # Demonstra a fila de prioridade baseada em Min-Heap.
    fila = MinHeap()
    for encomenda in encomendas:
        fila.inserir(encomenda)

    atendidas = []
    while not fila.vazio():
        atendidas.append(fila.remover())

    mostrar_encomendas(atendidas, "ORDEM DE ATENDIMENTO COM MIN-HEAP")
    print("\nOperacoes de reorganizacao do Min-Heap:", fila.operacoes)
