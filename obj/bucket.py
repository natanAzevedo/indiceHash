import sys


class Bucket:
    def __init__(self, capacidade: int):
        self.capacidade = capacidade
        self.entradas = []
        self.overflow_bucket = None
        self.nivel_overflow = 0  # Novo: rastrear níveis de overflow

    def esta_cheio(self):
        return len(self.entradas) >= self.capacidade

    def adicionar(self, chave: int, id_pag: int) -> bool:
        """Adiciona uma entrada ao bucket ou a um bucket de overflow, de forma iterativa."""
        bucket_atual = self
        houve_overflow_no_inicio = len(self.entradas) >= self.capacidade

        while True:
            if not bucket_atual.esta_cheio():
                bucket_atual.entradas.append((chave, id_pag))
                return houve_overflow_no_inicio

            if bucket_atual.overflow_bucket is None:
                bucket_atual.overflow_bucket = Bucket(self.capacidade)
                bucket_atual.overflow_bucket.nivel_overflow = bucket_atual.nivel_overflow + 1

            bucket_atual = bucket_atual.overflow_bucket
    def buscar_entrada(self, chave: int):
        """Busca uma entrada específica por chave - versão iterativa"""
        bucket_atual = self

        # Percorre toda a cadeia de overflow buckets
        while bucket_atual is not None:
            # Buscar no bucket atual
            for entrada_chave, id_pag in bucket_atual.entradas:
                if entrada_chave == chave:
                    return id_pag

            # Mover para o próximo overflow bucket
            bucket_atual = bucket_atual.overflow_bucket

        return None

    def get_total_entradas(self):
        """Retorna total de entradas incluindo overflows - versão iterativa"""
        total = 0
        bucket_atual = self

        # Percorre toda a cadeia somando as entradas
        while bucket_atual is not None:
            total += len(bucket_atual.entradas)
            bucket_atual = bucket_atual.overflow_bucket

        return total

    def get_max_nivel_overflow(self):
        """Retorna o nível máximo de overflow - versão iterativa"""
        max_nivel = self.nivel_overflow
        bucket_atual = self.overflow_bucket

        # Percorre a cadeia para encontrar o nível máximo
        while bucket_atual is not None:
            max_nivel = max(max_nivel, bucket_atual.nivel_overflow)
            bucket_atual = bucket_atual.overflow_bucket

        return max_nivel

    def get_buckets_na_cadeia(self):
        """Retorna todos os buckets na cadeia de overflow"""
        buckets = []
        bucket_atual = self

        while bucket_atual is not None:
            buckets.append(bucket_atual)
            bucket_atual = bucket_atual.overflow_bucket

        return buckets
