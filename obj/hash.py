import math

from obj.bucket import Bucket
from obj.table import Table


class Hash:
    def __init__(self, fr: int):
        self.fr = fr
        self.nr = 0
        self.nb = 0
        self.buckets = []
        self.total_colisoes = 0
        self.total_overflows = 0

    def funcao_hash(self, valor_str: str) -> int:
        hash_valor = sum(ord(c) for c in valor_str)
        return hash_valor % self.nb

    def construir(self, tabela: Table):
        dados_tabela = tabela.get_info_indice()
        self.nr = len(dados_tabela)

        if self.nr == 0 or self.fr <= 0:
            print("Não é possível construir o índice: sem dados ou FR inválido.")
            return

        self.nb = math.ceil(self.nr / self.fr)
        self.buckets = [Bucket(self.fr) for _ in range(self.nb)]

        for chave_id, valor_str, id_pag in dados_tabela:
            indice = self.funcao_hash(valor_str)
            bucket_alvo = self.buckets[indice]

            if len(bucket_alvo.entradas) > 0:
                self.total_colisoes += 1

            ocorreu_overflow = bucket_alvo.adicionar(chave_id, id_pag)
            if ocorreu_overflow:
                self.total_overflows += 1

    def buscar(self, valor_busca: str, tabela: Table):
        if not self.buckets:
            return None, 0

        indice = self.funcao_hash(valor_busca)
        bucket_atual = self.buckets[indice]

        paginas_a_visitar = set()

        while bucket_atual:
            for _, id_pag in bucket_atual.entradas:
                paginas_a_visitar.add(id_pag)
            bucket_atual = bucket_atual.overflow_bucket

        resultado = None
        custo = len(paginas_a_visitar)

        for id_pag in paginas_a_visitar:
            pagina = tabela.get_pagina(id_pag)
            if pagina:
                for tupla in pagina.get_tuplas():
                    if tupla.valor == valor_busca:
                        resultado = tupla
                        return resultado, custo, id_pag

        return None, custo, None

    def get_estatisticas(self):
        if self.nr == 0:
            return {
                "total_registros": 0,
                "total_colisoes": 0,
                "taxa_colisoes": 0,  # Mudança aqui: removido "(%) "
                "total_overflows": 0,
                "taxa_overflows": 0,  # Mudança aqui: removido "(%)"
                "total_buckets": 0,  # Campo adicionado
                "fator_carga": 0  # Campo adicionado
            }

        taxa_colisao = (self.total_colisoes / self.nr) * 100
        taxa_overflow = (self.total_overflows / self.nr) * 100
        fator_carga = self.nr / self.nb if self.nb > 0 else 0  # Novo cálculo

        return {
            "total_registros": self.nr,
            "total_buckets": self.nb,  # Campo adicionado
            "total_colisoes": self.total_colisoes,
            "taxa_colisoes": round(taxa_colisao, 2),  # Nome padronizado
            "total_overflows": self.total_overflows,
            "taxa_overflows": round(taxa_overflow, 2),  # Nome padronizado
            "fator_carga": round(fator_carga, 2)  # Campo adicionado
        }
