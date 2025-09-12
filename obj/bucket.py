class Bucket:
    def __init__(self, capacidade: int):
        self.capacidade = capacidade
        self.entradas = []
        self.overflow_bucket = None
        self.nivel_overflow = 0  # Novo: rastrear níveis de overflow

    def esta_cheio(self):
        return len(self.entradas) >= self.capacidade

    def adicionar(self, chave: int, id_pag: int) -> bool:
        """Retorna True se houve overflow"""
        if not self.esta_cheio():
            self.entradas.append((chave, id_pag))
            return False
        else:
            # Criar overflow bucket se necessário
            if self.overflow_bucket is None:
                self.overflow_bucket = Bucket(self.capacidade)
                self.overflow_bucket.nivel_overflow = self.nivel_overflow + 1

            # Adicionar recursivamente ao overflow bucket
            self.overflow_bucket.adicionar(chave, id_pag)
            return True  # Sempre retorna True pois houve overflow neste nível

    def buscar_entrada(self, chave: int):
        """Busca uma entrada específica por chave"""
        # Buscar no bucket atual
        for entrada_chave, id_pag in self.entradas:
            if entrada_chave == chave:
                return id_pag

        # Buscar nos overflow buckets
        if self.overflow_bucket:
            return self.overflow_bucket.buscar_entrada(chave)

        return None

    def get_total_entradas(self):
        """Retorna total de entradas incluindo overflows"""
        total = len(self.entradas)
        if self.overflow_bucket:
            total += self.overflow_bucket.get_total_entradas()
        return total

    def get_max_nivel_overflow(self):
        """Retorna o nível máximo de overflow"""
        if self.overflow_bucket:
            return max(self.nivel_overflow, self.overflow_bucket.get_max_nivel_overflow())
        return self.nivel_overflow
