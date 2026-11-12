"""
arvoreb.py - Arvore B de ordem m

Ordem m = maximo de filhos por no (m >= 3). Cada no tem no maximo m-1 chaves
e, exceto a raiz, no minimo ceil(m/2)-1. A insercao desce ate a folha
guardando o caminho na Pilha do grupo, insere, e sobe dividindo todo no que
passar de m-1 chaves. Chaves repetidas acumulam na lista de cargas.
Contador principal: nos visitados (cada no e um bloco de disco).
Nao usa bisect, dict nem sorted.
"""

from src.tads import Pilha


class NoB:
    def __init__(self, folha=True):
        self.chaves = []
        self.cargas = []    # cargas[i] = lista de cargas da chaves[i]
        self.filhos = []    # vazio nas folhas; len(chaves)+1 nos internos
        self.folha = folha


class ArvoreB:
    def __init__(self, m=3):
        if m < 3:
            raise ValueError("ordem m deve ser >= 3")
        self.m = m
        self.raiz = NoB()
        self.n_chaves = 0
        self.divisoes = 0         # acumulado das insercoes
        self.nos_visitados = 0    # acumulado das insercoes

    # ---- insercao -----------------------------------------------------------
    def inserir(self, chave, carga):
        pilha, no = Pilha(), self.raiz
        while True:
            self.nos_visitados += 1
            i = 0
            while i < len(no.chaves):
                if chave == no.chaves[i]:
                    no.cargas[i].append(carga)
                    return
                if chave < no.chaves[i]:
                    break
                i += 1
            if no.folha:
                break
            pilha.empilhar((no, i))
            no = no.filhos[i]
        no.chaves.insert(i, chave)
        no.cargas.insert(i, [carga])
        self.n_chaves += 1
        # sobe dividindo todo no que passou de m-1 chaves
        while len(no.chaves) > self.m - 1:
            meio = len(no.chaves) // 2
            direita = NoB(folha=no.folha)
            direita.chaves = no.chaves[meio + 1:]
            direita.cargas = no.cargas[meio + 1:]
            if not no.folha:
                direita.filhos = no.filhos[meio + 1:]
                no.filhos = no.filhos[:meio + 1]
            sobe_chave, sobe_carga = no.chaves[meio], no.cargas[meio]
            no.chaves, no.cargas = no.chaves[:meio], no.cargas[:meio]
            self.divisoes += 1
            if pilha.vazia():
                nova = NoB(folha=False)
                nova.chaves, nova.cargas = [sobe_chave], [sobe_carga]
                nova.filhos = [no, direita]
                self.raiz = nova
                return
            pai, j = pilha.desempilhar()
            pai.chaves.insert(j, sobe_chave)
            pai.cargas.insert(j, sobe_carga)
            pai.filhos.insert(j + 1, direita)
            no = pai

    # ---- busca --------------------------------------------------------------
    def buscar(self, chave):
        """Devolve (cargas, nos_visitados_desta_busca)."""
        visitados, no = 0, self.raiz
        while True:
            visitados += 1
            i = 0
            while i < len(no.chaves) and chave > no.chaves[i]:
                i += 1
            if i < len(no.chaves) and chave == no.chaves[i]:
                return no.cargas[i], visitados
            if no.folha:
                return [], visitados
            no = no.filhos[i]

    # ---- estatisticas -------------------------------------------------------
    def altura(self):
        """Numero de niveis (so a raiz = 1)."""
        h, no = 1, self.raiz
        while not no.folha:
            no = no.filhos[0]
            h += 1
        return h

    def contar_nos(self):
        total, pilha = 0, Pilha()
        pilha.empilhar(self.raiz)
        while not pilha.vazia():
            no = pilha.desempilhar()
            total += 1
            for f in no.filhos:
                pilha.empilhar(f)
        return total

    def ocupacao_media(self):
        """Fracao media de chaves por no em relacao ao maximo (m-1), de 0 a 1."""
        nos = self.contar_nos()
        return self.n_chaves / (nos * (self.m - 1))

    # ---- percurso -----------------------------------------------------------
    def em_ordem(self):
        """Lista de (chave, cargas) em ordem crescente, iterativo com Pilha.
        Mesmo formato de Arvore.em_ordem_com_pilha(), para conferir com a AVL."""
        saida, pilha = [], Pilha()
        pilha.empilhar((self.raiz, None))
        while not pilha.vazia():
            no, i = pilha.desempilhar()
            if i is not None:                  # emitir a chave i do no
                saida.append((no.chaves[i], no.cargas[i]))
            elif no.folha:
                for k in range(len(no.chaves)):
                    saida.append((no.chaves[k], no.cargas[k]))
            else:                              # empilha em ordem inversa
                for k in range(len(no.chaves) - 1, -1, -1):
                    pilha.empilhar((no.filhos[k + 1], None))
                    pilha.empilhar((no, k))
                pilha.empilhar((no.filhos[0], None))
        return saida

    # ---- invariantes --------------------------------------------------------
    def coerente(self):
        """True se: chaves estritamente crescentes em cada no e dentro dos
        limites herdados; ocupacao entre ceil(m/2)-1 e m-1 (raiz: >= 1 chave,
        exceto arvore vazia); filhos = chaves+1; TODAS as folhas no mesmo
        nivel; contador de chaves correto."""
        minimo = (self.m - 1) // 2
        nivel_folhas, contadas, pilha = None, 0, Pilha()
        pilha.empilhar((self.raiz, 1, None, None))
        while not pilha.vazia():
            no, nivel, lo, hi = pilha.desempilhar()
            k = len(no.chaves)
            contadas += k
            if k > self.m - 1 or len(no.cargas) != k:
                return False
            if any(not isinstance(cargas, list) or not cargas for cargas in no.cargas):
                return False
            if no is not self.raiz and k < minimo:
                return False
            if no is self.raiz and k == 0 and (self.n_chaves != 0 or not no.folha):
                return False
            for i in range(k):
                if i > 0 and no.chaves[i] <= no.chaves[i - 1]:
                    return False
                if lo is not None and no.chaves[i] <= lo:
                    return False
                if hi is not None and no.chaves[i] >= hi:
                    return False
            if no.folha:
                if no.filhos:
                    return False
                if nivel_folhas is None:
                    nivel_folhas = nivel
                elif nivel != nivel_folhas:
                    return False
            else:
                if len(no.filhos) != k + 1:
                    return False
                for i, f in enumerate(no.filhos):
                    l2 = no.chaves[i - 1] if i > 0 else lo
                    h2 = no.chaves[i] if i < k else hi
                    pilha.empilhar((f, nivel + 1, l2, h2))
        return contadas == self.n_chaves


# --------------------------------------------------------------------------
# VERIFICACAO (secao 7.7): unico lugar onde sorted() e listas simples entram.
# --------------------------------------------------------------------------
def verificar_contra_lista(arvore, reservas, campo="inicio"):
    chaves = sorted({r[campo] for r in reservas})
    pares = arvore.em_ordem()
    if [c for c, _ in pares] != chaves:
        return False
    for c in chaves:
        esperado = [r for r in reservas if r[campo] == c]
        if sorted(map(id, arvore.buscar(c)[0])) != sorted(map(id, esperado)):
            return False
    return arvore.coerente()