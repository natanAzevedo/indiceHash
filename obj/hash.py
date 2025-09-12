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
        """Função hash DJB2 - distribuição otimizada"""
        hash_valor = 5381
        for c in valor_str:
            hash_valor = ((hash_valor << 5) + hash_valor) + ord(c)
        return hash_valor % self.nb

    def construir(self, tabela: Table):
        dados_tabela = tabela.get_info_indice()
        self.nr = len(dados_tabela)

        if self.nr == 0 or self.fr <= 0:
            print("Não é possível construir o índice: sem dados ou FR inválido.")
            return

        self.nb = math.ceil(self.nr / self.fr)
        self.buckets = [Bucket(self.fr) for _ in range(self.nb)]

        # Resetar contadores
        self.total_colisoes = 0
        self.total_overflows = 0

        for chave_id, valor_str, id_pag in dados_tabela:
            indice = self.funcao_hash(valor_str)
            bucket_alvo = self.buckets[indice]

            # Contar colisão se bucket já tem entradas
            if len(bucket_alvo.entradas) > 0:
                self.total_colisoes += 1

            # Adicionar entrada ao bucket
            ocorreu_overflow = bucket_alvo.adicionar(chave_id, id_pag)
            if ocorreu_overflow:
                self.total_overflows += 1

    def buscar(self, valor_busca: str, tabela: Table):
        if not self.buckets:
            return None, 0, None

        indice = self.funcao_hash(valor_busca)
        paginas_a_visitar = set()

        # Busca no bucket original e seus overflows
        bucket_atual = self.buckets[indice]
        while bucket_atual:
            for _, id_pag in bucket_atual.entradas:
                paginas_a_visitar.add(id_pag)
            bucket_atual = bucket_atual.overflow_bucket

        # Buscar nas páginas coletadas
        custo = len(paginas_a_visitar)
        for id_pag in paginas_a_visitar:
            pagina = tabela.get_pagina(id_pag)
            if pagina:
                for tupla in pagina.get_tuplas():
                    if tupla.valor == valor_busca:
                        return tupla, custo, id_pag

        return None, custo, None

    def analisar_distribuicao(self):
        """Analisa a distribuição dos buckets"""
        distribuicao = {
            'buckets_vazios': 0,
            'buckets_parciais': 0,
            'buckets_cheios': 0,
            'buckets_com_overflow': 0,
            'max_entradas_bucket': 0,
            'min_entradas_bucket': float('inf'),
            'media_entradas': 0
        }

        total_entradas = 0

        for bucket in self.buckets:
            num_entradas = len(bucket.entradas)
            total_entradas += num_entradas

            if num_entradas == 0:
                distribuicao['buckets_vazios'] += 1
            elif num_entradas < self.fr:
                distribuicao['buckets_parciais'] += 1
            else:
                distribuicao['buckets_cheios'] += 1

            if bucket.overflow_bucket is not None:
                distribuicao['buckets_com_overflow'] += 1

            distribuicao['max_entradas_bucket'] = max(distribuicao['max_entradas_bucket'], num_entradas)
            if num_entradas > 0:
                distribuicao['min_entradas_bucket'] = min(distribuicao['min_entradas_bucket'], num_entradas)

        if total_entradas > 0:
            distribuicao['media_entradas'] = total_entradas / self.nb

        if distribuicao['min_entradas_bucket'] == float('inf'):
            distribuicao['min_entradas_bucket'] = 0

        return distribuicao

    def obter_estatisticas(self):
        if self.nr == 0:
            return {
                "total_registros": 0,
                "total_buckets": 0,
                "total_colisoes": 0,
                "taxa_colisoes": 0,
                "total_overflows": 0,
                "taxa_overflows": 0,
                "fator_carga": 0,
                "distribuicao": None
            }

        taxa_colisao = (self.total_colisoes / self.nr) * 100
        taxa_overflow = (self.total_overflows / self.nr) * 100
        fator_carga = self.nr / self.nb if self.nb > 0 else 0
        distribuicao = self.analisar_distribuicao()

        return {
            "total_registros": self.nr,
            "total_buckets": self.nb,
            "total_colisoes": self.total_colisoes,
            "taxa_colisoes": round(taxa_colisao, 2),
            "total_overflows": self.total_overflows,
            "taxa_overflows": round(taxa_overflow, 2),
            "fator_carga": round(fator_carga, 2),
            "distribuicao": distribuicao
        }

    def comparar_funcoes_hash(self, tabela: Table):
        """Analisa a distribuição da função hash atual"""
        dados_tabela = tabela.get_info_indice()

        if not dados_tabela:
            return None

        # Garantir que nb está definido para a função hash
        if self.nb == 0:
            self.nr = len(dados_tabela)
            self.nb = math.ceil(self.nr / self.fr)

        # Analisar apenas a função hash atual (DJB2)
        distribuicao = {}
        for _, valor_str, _ in dados_tabela:
            indice = self.funcao_hash(valor_str)
            distribuicao[indice] = distribuicao.get(indice, 0) + 1

        # Calcular estatísticas de distribuição
        valores = list(distribuicao.values())
        colisoes_teoricas = sum(max(0, v - 1) for v in valores)

        resultado = {
            'djb2': {
                'colisoes_teoricas': colisoes_teoricas,
                'buckets_utilizados': len(distribuicao),
                'max_por_bucket': max(valores) if valores else 0,
                'desvio_padrao': self._calcular_desvio_padrao(valores) if valores else 0
            }
        }

        return resultado

    def _calcular_desvio_padrao(self, valores):
        """Calcula desvio padrão"""
        if not valores:
            return 0

        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
        return math.sqrt(variancia)

    def obter_buckets(self):
        """Retorna lista de buckets para visualização"""
        return self.buckets

