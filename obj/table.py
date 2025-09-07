from obj.page import Page
from obj.tupla import Tupla


class Table:
    def __init__(self, arquivo: str):
        self.arquivo = arquivo
        self.paginas = []

    def carregar(self, tam_pagina: int):
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as file:
                id_pag = 0
                linhas = file.readlines()

                if not linhas:
                    return

                pagina_atual = Page(id=id_pag, capacidade=tam_pagina)
                self.paginas.append(pagina_atual)
                chave_id = 1
                for linha in linhas:
                    valor = linha.strip()
                    if not valor:
                        continue

                    tupla = Tupla(chave=chave_id, valor=valor)
                    chave_id += 1

                    if pagina_atual.esta_cheia():
                        id_pag += 1
                        pagina_atual = Page(id=id_pag, capacidade=tam_pagina)
                        self.paginas.append(pagina_atual)

                    pagina_atual.adicionar_tupla(tupla)
        except FileNotFoundError:
            print(f"ERRO: O arquivo '{self.arquivo}' não foi encontrado.")
            exit()

    def get_info_indice(self):
        info = []
        for pagina in self.paginas:
            for tupla in pagina.tuplas:
                info.append((tupla.chave, tupla.valor, pagina.id))
        return info

    def table_scan(self, valor_busca: str):
        custo = 0
        for pagina in self.paginas:
            custo += 1
            for tupla in pagina.get_tuplas():
                if tupla.valor == valor_busca:
                    return tupla, custo

        return None, custo

    def table_scan_detailed(self, valor_busca: str):
        custo = 0
        scanned_records = []
        for pagina in self.paginas:
            custo += 1
            for tupla in pagina.get_tuplas():
                scanned_records.append(tupla.valor)  # Adiciona o valor da tupla escaneada
                if tupla.valor == valor_busca:
                    return tupla, custo, scanned_records
        return None, custo, scanned_records

    def get_total_pag(self) -> int:
        return len(self.paginas)

    def get_total_tuplas(self) -> int:
        return sum(len(p.tuplas) for p in self.paginas)

    def get_pagina(self, id_pagina: int) -> Page | None:
        if 0 <= id_pagina < len(self.paginas):
            return self.paginas[id_pagina]
        return None
