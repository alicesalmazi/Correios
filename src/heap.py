"""
heap.py
Heap mínimo e Heapsort aplicados ao sistema de encomendas do UNASP.

A estrutura MinHeap utiliza a TAD Lista definida em tads.py.
Não utiliza heapq, sorted(), sort() ou bibliotecas de ordenação.
"""

import json
from datetime import datetime, timezone
from src.tads import Lista


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
    """Retorna a prioridade da categoria do destinatário."""
    destinatario = encomenda.get("destinatario", {})
    categoria = destinatario.get("categoriaPublico", "").strip().upper()
    return PRIORIDADES.get(categoria, 4)


def converter_data(data):
    """Converte datas conhecidas para datetime comparável."""
    if not data:
        return datetime.max

    if isinstance(data, datetime):
        resultado = data
    else:
        texto = str(data).strip()
        formatos = (
            "%d/%m/%Y",
            "%d/%m/%Y %H:%M:%S",
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S"
        )
        resultado = None

        for formato in formatos:
            try:
                resultado = datetime.strptime(texto, formato)
                break
            except ValueError:
                continue

        if resultado is None:
            try:
                resultado = datetime.fromisoformat(texto.replace("Z", "+00:00"))
            except ValueError:
                return datetime.max

    # Evita erro ao comparar datas com e sem fuso horário.
    if resultado.tzinfo is not None:
        resultado = resultado.astimezone(timezone.utc).replace(tzinfo=None)

    return resultado


def chave_da_encomenda(encomenda):
    """
    Ordem de atendimento:
    1) menor número de prioridade;
    2) data de chegada mais antiga;
    3) número da etiqueta em ordem crescente.
    """
    data = converter_data(encomenda.get("dataChegada"))
    etiqueta = str(encomenda.get("numEtiqueta", ""))
    return (prioridade_da_encomenda(encomenda), data, etiqueta)


class MinHeap:
    """Heap mínimo: o elemento de menor chave permanece na raiz."""

    def __init__(self, chave=None):
        self.elementos = Lista()
        self.chave = chave if chave is not None else chave_da_encomenda
        self.comparacoes = 0
        self.trocas = 0

    def vazio(self):
        return self.elementos.tamanho == 0

    def tamanho(self):
        return self.elementos.tamanho

    def _comparar(self, primeiro, segundo):
        """Compara dois elementos e contabiliza somente a comparação."""
        self.comparacoes += 1
        return self.chave(primeiro) < self.chave(segundo)

    def _trocar(self, indice_a, indice_b):
        """Troca dois elementos e contabiliza somente a troca."""
        elemento_a = self.elementos.obter(indice_a)
        elemento_b = self.elementos.obter(indice_b)
        self.elementos.modificar(indice_a, elemento_b)
        self.elementos.modificar(indice_b, elemento_a)
        self.trocas += 1

    def inserir(self, elemento):
        """Insere no final e reorganiza o Heap de baixo para cima."""
        self.elementos.adicionar(elemento)
        self._subir(self.elementos.tamanho - 1)

    def _subir(self, indice):
        while indice > 0:
            pai = (indice - 1) // 2
            atual = self.elementos.obter(indice)
            elemento_pai = self.elementos.obter(pai)

            if self._comparar(atual, elemento_pai):
                self._trocar(indice, pai)
                indice = pai
            else:
                break

    def remover(self):
        """Remove e retorna a raiz, que é o menor elemento."""
        if self.vazio():
            return None

        if self.elementos.tamanho == 1:
            return self.elementos.remover(0)

        menor = self.elementos.obter(0)
        ultimo = self.elementos.remover(self.elementos.tamanho - 1)
        self.elementos.modificar(0, ultimo)
        self._descer(0)
        return menor

    def _descer(self, indice):
        """Restaura a propriedade de Min-Heap a partir de um índice."""
        tamanho_atual = self.elementos.tamanho

        while True:
            menor = indice
            esquerdo = 2 * indice + 1
            direito = 2 * indice + 2

            elemento_menor = self.elementos.obter(menor)

            if esquerdo < tamanho_atual:
                elemento_esquerdo = self.elementos.obter(esquerdo)
                if self._comparar(elemento_esquerdo, elemento_menor):
                    menor = esquerdo
                    elemento_menor = elemento_esquerdo

            if direito < tamanho_atual:
                elemento_direito = self.elementos.obter(direito)
                if self._comparar(elemento_direito, elemento_menor):
                    menor = direito

            if menor == indice:
                break

            self._trocar(indice, menor)
            indice = menor

    def coerente(self):
        """
        Verifica todo o Heap.
        Retorna False se algum filho for menor que seu pai.
        As comparações realizadas aqui também são contabilizadas.
        """
        for indice in range(1, self.elementos.tamanho):
            pai = (indice - 1) // 2
            filho = self.elementos.obter(indice)
            elemento_pai = self.elementos.obter(pai)

            if self._comparar(filho, elemento_pai):
                return False

        return True

    def reiniciar_contadores(self):
        """Zera separadamente os contadores de comparações e trocas."""
        self.comparacoes = 0
        self.trocas = 0


def k_menores_com_heap(itens, k, chave=None):
    """
    Retorna os k menores elementos usando MinHeap.

    Constrói o Heap com os itens e realiza somente k remoções.
    Portanto, não ordena toda a coleção quando k é menor que a
    quantidade total de itens.
    """
    if k < 0:
        raise ValueError("k não pode ser negativo.")

    heap = MinHeap(chave=chave)

    for item in itens:
        heap.inserir(item)

    resultado = []
    quantidade = min(k, heap.tamanho())

    for _ in range(quantidade):
        resultado.append(heap.remover())

    return resultado


def heapsort(encomendas):
    """
    Ordena as encomendas em ordem crescente de prioridade usando
    Max-Heap. A estrutura auxiliar é a TAD Lista.
    Retorna uma lista Python para facilitar a exibição/integração.
    """
    dados = Lista()
    for encomenda in encomendas:
        dados.adicionar(encomenda)

    tamanho = dados.tamanho

    def comparar_maior(i, j):
        return chave_da_encomenda(dados.obter(i)) > chave_da_encomenda(dados.obter(j))

    def trocar(i, j):
        a = dados.obter(i)
        b = dados.obter(j)
        dados.modificar(i, b)
        dados.modificar(j, a)

    def descer_maximo(raiz, limite):
        while True:
            maior = raiz
            esquerdo = 2 * raiz + 1
            direito = 2 * raiz + 2

            if esquerdo < limite and comparar_maior(esquerdo, maior):
                maior = esquerdo

            if direito < limite and comparar_maior(direito, maior):
                maior = direito

            if maior == raiz:
                break

            trocar(raiz, maior)
            raiz = maior

    # Constrói o Max-Heap.
    indice = tamanho // 2 - 1
    while indice >= 0:
        descer_maximo(indice, tamanho)
        indice -= 1

    # Extrai o maior para o final, formando a ordem crescente.
    fim = tamanho - 1
    while fim > 0:
        trocar(0, fim)
        descer_maximo(0, fim)
        fim -= 1

    return dados.para_lista()


def carregar_encomendas(caminho="json/encomenda.json"):
    """Carrega um objeto ou uma lista de encomendas de um JSON."""
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if isinstance(dados, list):
        return dados
    return [dados]


def mostrar_encomendas(encomendas, titulo):
    print("\n" + titulo)

    if not encomendas:
        print("Nenhuma encomenda cadastrada.")
        return

    for encomenda in encomendas:
        destinatario = encomenda.get("destinatario", {})
        print(
            "Prioridade:", prioridade_da_encomenda(encomenda),
            "| Etiqueta:", encomenda.get("numEtiqueta", "Sem etiqueta"),
            "| Destinatário:", destinatario.get("nome", "Não informado"),
            "| Categoria:", destinatario.get("categoriaPublico", "Não informada"),
            "| Data:", encomenda.get("dataChegada", "Não informada")
        )


if __name__ == "__main__":
    encomendas = carregar_encomendas()

    ordenadas = heapsort(encomendas)
    mostrar_encomendas(ordenadas, "ENCOMENDAS ORDENADAS COM HEAPSORT")

    fila_prioridade = MinHeap(chave=chave_da_encomenda)
    for encomenda in encomendas:
        fila_prioridade.inserir(encomenda)

    print("\nHeap coerente após as inserções?", fila_prioridade.coerente())

    atendidas = []
    while not fila_prioridade.vazio():
        atendidas.append(fila_prioridade.remover())

    mostrar_encomendas(atendidas, "ORDEM DE ATENDIMENTO COM MIN-HEAP")
    print("\nComparações:", fila_prioridade.comparacoes)
    print("Trocas:", fila_prioridade.trocas)