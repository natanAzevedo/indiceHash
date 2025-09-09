import math
import hashlib
from obj.bucket import Bucket
from obj.table import Table


class Hash:
    def __init__(self, fr: int, metodo_colisao='overflow'):
        self.fr = fr
        self.nr = 0
        self.nb = 0
        self.buckets = []
        self.total_colisoes = 0
        self.total_overflows = 0
        self.metodo_colisao = metodo_colisao  # 'overflow', 'linear_probing', 'quadratic_probing'

    def funcao_hash_simples(self, valor_str: str) -> int:
        """Função hash original - mantida para compatibilidade"""
        hash_valor = sum(ord(c) for c in valor_str)
        return hash_valor % self.nb

    def funcao_hash_melhorada(self, valor_str: str) -> int:
        """Função hash melhorada usando SHA-256"""
        hash_obj = hashlib.sha256(valor_str.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        hash_int = int(hash_hex[:8], 16)  # Usa apenas os primeiros 8 caracteres
        return hash_int % self.nb

    def funcao_hash_djb2(self, valor_str: str) -> int:
        """Função hash DJB2 - boa distribuição"""
        hash_valor = 5381
        for c in valor_str:
            hash_valor = ((hash_valor << 5) + hash_valor) + ord(c)
        return hash_valor % self.nb

    def funcao_hash(self, valor_str: str) -> int:
        """Função hash principal - usa DJB2 por padrão"""
        return self.funcao_hash_djb2(valor_str)

    def linear_probing(self, indice_inicial: int) -> int:
        """Implementa linear probing para encontrar próxima posição livre"""
        indice = indice_inicial
        tentativas = 0

        while tentativas < self.nb:
            if not self.buckets[indice].esta_cheio():
                return indice
            indice = (indice + 1) % self.nb
            tentativas += 1

        # Se todos os buckets estão cheios, retorna o índice original
        return indice_inicial

    def quadratic_probing(self, indice_inicial: int) -> int:
        """Implementa quadratic probing para encontrar próxima posição livre"""
        for i in range(self.nb):
            indice = (indice_inicial + i * i) % self.nb
            if not self.buckets[indice].esta_cheio():
                return indice

        # Se não encontrar posição livre, retorna o índice original
        return indice_inicial

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
            indice_original = self.funcao_hash(valor_str)
            indice_final = indice_original

            # Aplicar estratégia de tratamento de colisões
            if self.metodo_colisao == 'linear_probing':
                indice_final = self.linear_probing(indice_original)
            elif self.metodo_colisao == 'quadratic_probing':
                indice_final = self.quadratic_probing(indice_original)

            # Verificar se houve colisão (posição já ocupada)
            bucket_alvo = self.buckets[indice_final]

            # Contar colisão se bucket já tem entradas OU se mudou de posição
            if len(bucket_alvo.entradas) > 0 or indice_final != indice_original:
                self.total_colisoes += 1

            # Adicionar entrada ao bucket
            ocorreu_overflow = bucket_alvo.adicionar(chave_id, id_pag)
            if ocorreu_overflow:
                self.total_overflows += 1

    def buscar(self, valor_busca: str, tabela: Table):
        if not self.buckets:
            return None, 0, None

        indice_original = self.funcao_hash(valor_busca)
        paginas_a_visitar = set()

        if self.metodo_colisao == 'overflow':
            # Busca apenas no bucket original e seus overflows
            bucket_atual = self.buckets[indice_original]
            while bucket_atual:
                for _, id_pag in bucket_atual.entradas:
                    paginas_a_visitar.add(id_pag)
                bucket_atual = bucket_atual.overflow_bucket

        else:
            # Para probing, precisa verificar múltiplas posições
            posicoes_verificar = []

            if self.metodo_colisao == 'linear_probing':
                for i in range(self.nb):
                    pos = (indice_original + i) % self.nb
                    posicoes_verificar.append(pos)
                    if len(self.buckets[pos].entradas) == 0:
                        break  # Para quando encontrar bucket vazio

            elif self.metodo_colisao == 'quadratic_probing':
                for i in range(self.nb):
                    pos = (indice_original + i * i) % self.nb
                    posicoes_verificar.append(pos)
                    if len(self.buckets[pos].entradas) == 0:
                        break  # Para quando encontrar bucket vazio

            # Coletar páginas de todas as posições relevantes
            for pos in posicoes_verificar:
                bucket_atual = self.buckets[pos]
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

    def get_estatisticas(self):
        if self.nr == 0:
            return {
                "total_registros": 0,
                "total_buckets": 0,
                "total_colisoes": 0,
                "taxa_colisoes": 0,
                "total_overflows": 0,
                "taxa_overflows": 0,
                "fator_carga": 0,
                "metodo_colisao": self.metodo_colisao,
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
            "metodo_colisao": self.metodo_colisao,
            "distribuicao": distribuicao
        }

    def comparar_funcoes_hash(self, tabela: Table):
        """Compara diferentes funções hash"""
        dados_tabela = tabela.get_info_indice()

        if not dados_tabela:
            return None

        funcoes = {
            'simples': self.funcao_hash_simples,
            'djb2': self.funcao_hash_djb2,
            'sha256': self.funcao_hash_melhorada
        }

        resultados = {}

        for nome, funcao in funcoes.items():
            distribuicao = {}
            for _, valor_str, _ in dados_tabela:
                indice = funcao(valor_str)
                distribuicao[indice] = distribuicao.get(indice, 0) + 1

            # Calcular estatísticas de distribuição
            valores = list(distribuicao.values())
            colisoes_teoricas = sum(max(0, v - 1) for v in valores)

            resultados[nome] = {
                'colisoes_teoricas': colisoes_teoricas,
                'buckets_utilizados': len(distribuicao),
                'max_por_bucket': max(valores) if valores else 0,
                'desvio_padrao': self._calcular_desvio_padrao(valores) if valores else 0
            }

        return resultados

    def _calcular_desvio_padrao(self, valores):
        """Calcula desvio padrão"""
        if not valores:
            return 0

        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
        return math.sqrt(variancia)

    @staticmethod
    def testar_metodos_colisao(tabela: Table, fr: int = 3):
        """Testa diferentes métodos de tratamento de colisões"""
        metodos = ['overflow', 'linear_probing', 'quadratic_probing']
        resultados = {}

        for metodo in metodos:
            print(f"\n=== Testando {metodo.upper()} ===")

            hash_index = Hash(fr, metodo_colisao=metodo)
            hash_index.construir(tabela)

            stats = hash_index.get_estatisticas()
            resultados[metodo] = stats

            print(f"Colisões: {stats['total_colisoes']} ({stats['taxa_colisoes']}%)")
            print(f"Overflows: {stats['total_overflows']} ({stats['taxa_overflows']}%)")
            print(f"Fator de carga: {stats['fator_carga']}")
            print(f"Buckets vazios: {stats['distribuicao']['buckets_vazios']}")

        return resultados

    def get_buckets(self):
        """Retorna lista de buckets para visualização"""
        return self.buckets

