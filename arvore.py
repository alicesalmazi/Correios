"""Arvore binaria de busca, com balanceamento AVL opcional."""

from tads import Fila, Pilha
from arvoreb import ArvoreB, NoB


class No:
    def __init__(self, chave, carga):
        self.chave = chave
        self.cargas = [carga]
        self.esquerda = None
        self.direita = None
        self.altura = 1


class Arvore:
    def __init__(self, balanceada=False):
        self.balanceada = balanceada
        self.raiz = None
        self.comparacoes = 0
        self.rotacoes = 0
        self.n_nos = 0
        self.n_chaves = 0

    @staticmethod
    def _altura(no):
        return no.altura if no is not None else 0

    @classmethod
    def _atualizar_altura(cls, no):
        no.altura = 1 + max(cls._altura(no.esquerda), cls._altura(no.direita))

    @classmethod
    def _fator_balanceamento(cls, no):
        return cls._altura(no.esquerda) - cls._altura(no.direita)

    def _rotacionar_direita(self, raiz):
        nova_raiz = raiz.esquerda
        raiz.esquerda = nova_raiz.direita
        nova_raiz.direita = raiz
        self._atualizar_altura(raiz)
        self._atualizar_altura(nova_raiz)
        self.rotacoes += 1
        return nova_raiz

    def _rotacionar_esquerda(self, raiz):
        nova_raiz = raiz.direita
        raiz.direita = nova_raiz.esquerda
        nova_raiz.esquerda = raiz
        self._atualizar_altura(raiz)
        self._atualizar_altura(nova_raiz)
        self.rotacoes += 1
        return nova_raiz

    def _rebalancear(self, no):
        fator = self._fator_balanceamento(no)
        if fator > 1:
            if self._fator_balanceamento(no.esquerda) < 0:
                no.esquerda = self._rotacionar_esquerda(no.esquerda)
            return self._rotacionar_direita(no)
        if fator < -1:
            if self._fator_balanceamento(no.direita) > 0:
                no.direita = self._rotacionar_direita(no.direita)
            return self._rotacionar_esquerda(no)
        return no

    def inserir(self, chave, carga):
        if self.raiz is None:
            self.raiz = No(chave, carga)
            self.n_nos = 1
            self.n_chaves = 1
            return

        caminho = []
        no = self.raiz
        while no is not None:
            self.comparacoes += 1
            if chave == no.chave:
                no.cargas.append(carga)
                return

            self.comparacoes += 1
            if chave < no.chave:
                caminho.append((no, "esquerda"))
                if no.esquerda is None:
                    no.esquerda = No(chave, carga)
                    break
                no = no.esquerda
            else:
                caminho.append((no, "direita"))
                if no.direita is None:
                    no.direita = No(chave, carga)
                    break
                no = no.direita

        self.n_nos += 1
        self.n_chaves += 1
        for indice in range(len(caminho) - 1, -1, -1):
            atual = caminho[indice][0]
            self._atualizar_altura(atual)
            if self.balanceada:
                nova_raiz = self._rebalancear(atual)
                if indice == 0:
                    self.raiz = nova_raiz
                else:
                    pai, lado = caminho[indice - 1]
                    setattr(pai, lado, nova_raiz)

    def buscar(self, chave):
        comparacoes_iniciais = self.comparacoes
        no = self.raiz
        while no is not None:
            self.comparacoes += 1
            if chave == no.chave:
                return no.cargas, self.comparacoes - comparacoes_iniciais
            self.comparacoes += 1
            no = no.esquerda if chave < no.chave else no.direita
        return [], self.comparacoes - comparacoes_iniciais

    def faixa(self, inicio, fim):
        cargas = []
        visitados = 0
        self.comparacoes += 1
        if inicio > fim:
            return cargas, visitados

        pilha = Pilha()
        no = self.raiz
        while no is not None or not pilha.vazia():
            while no is not None:
                visitados += 1
                self.comparacoes += 1
                if no.chave >= inicio:
                    pilha.empilhar(no)
                    no = no.esquerda
                else:
                    no = no.direita

            if pilha.vazia():
                break
            no = pilha.desempilhar()
            self.comparacoes += 1
            if no.chave > fim:
                break
            cargas.extend(no.cargas)
            no = no.direita
        return cargas, visitados

    def predecessor(self, chave):
        candidato = None
        no = self.raiz
        while no is not None:
            self.comparacoes += 1
            if no.chave < chave:
                candidato = no
                no = no.direita
            else:
                no = no.esquerda
        return candidato.chave if candidato is not None else None

    def altura(self):
        return self._altura(self.raiz)

    def caminho_medio(self):
        if self.n_nos == 0:
            return 0

        soma_niveis = 0
        fila = Fila()
        fila.enfileirar((self.raiz, 1))
        while not fila.vazia():
            no, nivel = fila.desenfileirar()
            soma_niveis += nivel
            if no.esquerda is not None:
                fila.enfileirar((no.esquerda, nivel + 1))
            if no.direita is not None:
                fila.enfileirar((no.direita, nivel + 1))
        return soma_niveis / self.n_nos

    def em_ordem_com_pilha(self):
        saida = []
        pilha = Pilha()
        no = self.raiz
        while no is not None or not pilha.vazia():
            while no is not None:
                pilha.empilhar(no)
                no = no.esquerda
            no = pilha.desempilhar()
            saida.append((no.chave, no.cargas))
            no = no.direita
        return saida

    def em_largura_com_fila(self):
        saida = []
        if self.raiz is None:
            return saida

        fila = Fila()
        fila.enfileirar(self.raiz)
        while not fila.vazia():
            no = fila.desenfileirar()
            saida.append((no.chave, no.cargas))
            if no.esquerda is not None:
                fila.enfileirar(no.esquerda)
            if no.direita is not None:
                fila.enfileirar(no.direita)
        return saida

    def coerente(self):
        contagem, pilha = 0, Pilha()
        pilha.empilhar((self.raiz, None, None))
        while not pilha.vazia():
            no, limite_inferior, limite_superior = pilha.desempilhar()
            if no is None:
                continue
            contagem += 1

            if not no.cargas:
                return False
            if limite_inferior is not None and no.chave <= limite_inferior:
                return False
            if limite_superior is not None and no.chave >= limite_superior:
                return False

            altura_esquerda = self._altura(no.esquerda)
            altura_direita = self._altura(no.direita)
            if no.altura != 1 + max(altura_esquerda, altura_direita):
                return False
            if self.balanceada and abs(altura_esquerda - altura_direita) > 1:
                return False

            pilha.empilhar((no.esquerda, limite_inferior, no.chave))
            pilha.empilhar((no.direita, no.chave, limite_superior))

        return contagem == self.n_nos == self.n_chaves


def verificar_contra_lista(arvore, reservas, campo="inicio"):
    chaves = sorted({reserva[campo] for reserva in reservas})
    pares = arvore.em_ordem_com_pilha()
    if [chave for chave, _ in pares] != chaves:
        return False
    for chave in chaves:
        esperado = [reserva for reserva in reservas if reserva[campo] == chave]
        cargas, _ = arvore.buscar(chave)
        if sorted(map(id, cargas)) != sorted(map(id, esperado)):
            return False
    return arvore.coerente()
