"""
tads.py
Implementação dos Tipos Abstratos de Dados (TADs):
Lista, Fila e Pilha.

Projeto: Central de Reservas - UNASP EC
Estrutura de Dados II - 2026/2
"""


class No:
    """Nó utilizado nas estruturas Fila e Pilha."""

    def __init__(self, valor):
        self.valor = valor
        self.proximo = None


class Lista:
    """
    Lista sequencial encapsulada.

    O armazenamento interno fica protegido nesta classe. As outras
    estruturas devem acessar os elementos pelos métodos da TAD.
    """

    def __init__(self):
        self._elementos = []

    @property
    def tamanho(self):
        """Quantidade de elementos armazenados."""
        return len(self._elementos)

    def inserir(self, indice, valor):
        """Insere valor na posição indicada."""
        if indice < 0 or indice > self.tamanho:
            raise IndexError("Índice inválido para inserção.")
        self._elementos.insert(indice, valor)

    def obter(self, indice):
        """Retorna o elemento da posição indicada."""
        if indice < 0 or indice >= self.tamanho:
            raise IndexError("Índice inválido para consulta.")
        return self._elementos[indice]

    def modificar(self, indice, valor):
        """Substitui o elemento da posição indicada."""
        if indice < 0 or indice >= self.tamanho:
            raise IndexError("Índice inválido para modificação.")
        self._elementos[indice] = valor

    def remover(self, indice):
        """Remove e retorna o elemento da posição indicada."""
        if indice < 0 or indice >= self.tamanho:
            raise IndexError("Índice inválido para remoção.")
        return self._elementos.pop(indice)

    def adicionar(self, valor):
        """Adiciona um elemento ao final da lista."""
        self.inserir(self.tamanho, valor)

    def vazia(self):
        return self.tamanho == 0

    def para_lista(self):
        """Devolve uma cópia em lista Python para integração/saída."""
        return self._elementos.copy()

    def __iter__(self):
        return iter(self._elementos)


class Fila:
    """
    Fila encadeada (FIFO).
    O primeiro elemento inserido é o primeiro a sair.
    """

    def __init__(self):
        self.inicio = None
        self.fim = None
        self._tamanho = 0
        self.operacoes = 0

    def enfileirar(self, valor):
        """Adiciona um elemento ao final da fila em O(1)."""
        novo = No(valor)

        if self.vazia_sem_contar():
            self.inicio = novo
            self.fim = novo
        else:
            self.fim.proximo = novo
            self.fim = novo

        self._tamanho += 1
        self.operacoes += 1

    def desenfileirar(self):
        """Remove e retorna o primeiro elemento em O(1)."""
        self.operacoes += 1

        if self.inicio is None:
            raise IndexError("Não é possível desenfileirar uma fila vazia.")

        valor = self.inicio.valor
        self.inicio = self.inicio.proximo
        self._tamanho -= 1

        if self.inicio is None:
            self.fim = None

        return valor

    def frente(self):
        """Retorna o primeiro elemento sem removê-lo."""
        self.operacoes += 1

        if self.inicio is None:
            raise IndexError("A fila está vazia.")

        return self.inicio.valor

    def vazia_sem_contar(self):
        """Verificação interna sem alterar o contador."""
        return self.inicio is None

    def vazia(self):
        """Verifica se a fila está vazia."""
        self.operacoes += 1
        return self.vazia_sem_contar()

    def tamanho(self):
        """Retorna a quantidade de elementos da fila."""
        self.operacoes += 1
        return self._tamanho


class Pilha:
    """
    Pilha encadeada (LIFO).
    O último elemento inserido é o primeiro a sair.
    """

    def __init__(self):
        self.topo = None
        self._tamanho = 0
        self.operacoes = 0

    def empilhar(self, valor):
        """Adiciona um elemento ao topo da pilha em O(1)."""
        novo = No(valor)
        novo.proximo = self.topo
        self.topo = novo
        self._tamanho += 1
        self.operacoes += 1

    def desempilhar(self):
        """Remove e retorna o elemento do topo em O(1)."""
        self.operacoes += 1

        if self.topo is None:
            raise IndexError("Não é possível desempilhar uma pilha vazia.")

        valor = self.topo.valor
        self.topo = self.topo.proximo
        self._tamanho -= 1
        return valor

    def espiar(self):
        """Retorna o elemento do topo sem removê-lo."""
        self.operacoes += 1

        if self.topo is None:
            raise IndexError("A pilha está vazia.")

        return self.topo.valor

    def vazia(self):
        """Verifica se a pilha está vazia."""
        self.operacoes += 1
        return self.topo is None

    def tamanho(self):
        """Retorna a quantidade de elementos da pilha."""
        self.operacoes += 1
        return self._tamanho
