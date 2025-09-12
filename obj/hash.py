import math
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

    def funcao_hash(self, valor_str: str) -> int:
        """Função hash DJB2 - distribuição otimizada"""
        hash_valor = 5381
        for c in valor_str:
            hash_valor = ((hash_valor << 5) + hash_valor) + ord(c)
        return hash_valor % self.nb

    def sondagem_linear(self, indice_inicial: int) -> int:
        """Implementa sondagem linear para encontrar próxima posição livre"""
        indice = indice_inicial
        tentativas = 0

        while tentativas < self.nb:
            if not self.buckets[indice].esta_cheio():
                return indice
            indice = (indice + 1) % self.nb
            tentativas += 1

        # Se todos os buckets estão cheios, retorna o índice original
        return indice_inicial

    def sondagem_quadratica(self, indice_inicial: int) -> int:
        """Implementa sondagem quadrática para encontrar próxima posição livre"""
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
                indice_final = self.sondagem_linear(indice_original)
            elif self.metodo_colisao == 'quadratic_probing':
                indice_final = self.sondagem_quadratica(indice_original)

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
            # Para probing, busca mais eficiente
            posicoes_verificar = []

            if self.metodo_colisao == 'linear_probing':
                # Busca linear até encontrar bucket vazio ou limite razoável
                limite_busca = min(100, self.nb)  # Limita busca para evitar percorrer tudo
                for i in range(limite_busca):
                    pos = (indice_original + i) % self.nb
                    bucket = self.buckets[pos]
                    
                    # Se bucket tem entradas, verificar se pode conter nossa chave
                    if len(bucket.entradas) > 0:
                        posicoes_verificar.append(pos)
                    else:
                        # Bucket vazio = fim da sequência de probing
                        break

            elif self.metodo_colisao == 'quadratic_probing':
                # Busca quadrática com limite
                limite_busca = min(100, self.nb)
                for i in range(limite_busca):
                    pos = (indice_original + i * i) % self.nb
                    bucket = self.buckets[pos]
                    
                    if len(bucket.entradas) > 0:
                        posicoes_verificar.append(pos)
                    else:
                        break

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

    @staticmethod
    def testar_metodos_colisao(tabela: Table, fr: int = 3):
        """Testa diferentes métodos de tratamento de colisões"""
        metodos = ['overflow', 'linear_probing', 'quadratic_probing']
        resultados = {}

        for metodo in metodos:
            print(f"\n=== Testando {metodo.upper()} ===")

            hash_index = Hash(fr, metodo_colisao=metodo)
            hash_index.construir(tabela)

            stats = hash_index.obter_estatisticas()
            resultados[metodo] = stats

            print(f"Colisões: {stats['total_colisoes']} ({stats['taxa_colisoes']}%)")
            print(f"Overflows: {stats['total_overflows']} ({stats['taxa_overflows']}%)")
            print(f"Fator de carga: {stats['fator_carga']}")
            print(f"Buckets vazios: {stats['distribuicao']['buckets_vazios']}")

        return resultados

    def obter_buckets(self):
        """Retorna lista de buckets para visualização"""
        return self.buckets

