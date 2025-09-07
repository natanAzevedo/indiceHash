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

    def table_scan_detailed(self, valor_busca: str, max_records_to_show=100):
        custo = 0
        scanned_records = []
        total_records_scanned = 0
        found = False

        for pagina in self.paginas:
            custo += 1
            for tupla in pagina.get_tuplas():
                total_records_scanned += 1

                # Só adiciona registros para visualização se ainda não atingiu o limite
                if len(scanned_records) < max_records_to_show:
                    scanned_records.append({
                        "index": total_records_scanned,
                        "value": tupla.valor,
                        "page": pagina.id
                    })

                # Verifica se encontrou o valor
                if tupla.valor == valor_busca:
                    found = True
                    result_tupla = tupla
                    # Adiciona o registro encontrado se não estiver na lista
                    if len(scanned_records) == max_records_to_show and not any(
                            r["value"] == tupla.valor for r in scanned_records):
                        scanned_records.append({
                            "index": total_records_scanned,
                            "value": tupla.valor,
                            "page": pagina.id,
                            "found": True
                        })
                    return result_tupla, custo, {
                        "records": scanned_records,
                        "total_scanned": total_records_scanned,
                        "limited": total_records_scanned > max_records_to_show
                    }

        return None, custo, {
            "records": scanned_records,
            "total_scanned": total_records_scanned,
            "limited": total_records_scanned > max_records_to_show
        }
    def get_total_pag(self) -> int:
        return len(self.paginas)

    def get_total_tuplas(self) -> int:
        return sum(len(p.tuplas) for p in self.paginas)

    def get_pagina(self, id_pagina: int) -> Page | None:
        if 0 <= id_pagina < len(self.paginas):
            return self.paginas[id_pagina]
        return None
