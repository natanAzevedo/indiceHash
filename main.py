import time

from obj.hash import Hash
from obj.table import Table

if __name__ == "__main__":  
    # 1. Definir o nome do arquivo a ser lido
    NOME_ARQUIVO = "words.txt"

    # 2. Carregar os dados na tabela
    tamanho_pagina = 100 # Quantas palavras por página
    tabela = Table(NOME_ARQUIVO)
    tabela.carregar(tam_pagina=tamanho_pagina)
    
    # Só continua se a tabela tiver sido carregada com sucesso
    if tabela.get_total_tuplas() > 0:
        print(f"Arquivo '{NOME_ARQUIVO}' carregado com sucesso!")
        print(f"Total de Tuplas: {tabela.get_total_tuplas()}")
        print(f"Total de Páginas: {tabela.get_total_pag()}")
        print("-" * 30)

        # 3. Construir o índice hash com configuração otimizada
        tamanho_bucket_fr = 5  # Otimizado: configuração de máxima eficiência
        indice_hash = Hash(fr=tamanho_bucket_fr)
        indice_hash.construir(tabela)

        # 4. Exibir estatísticas melhoradas
        estatisticas = indice_hash.obter_estatisticas()
        print("=== Estatísticas do Índice Hash (CONFIGURAÇÃO OTIMIZADA) ===")
        print(f"  Total de Registros: {estatisticas['total_registros']:,}")
        print(f"  Total de Buckets: {estatisticas['total_buckets']:,}")
        print(f"  Fator de Carga: {estatisticas['fator_carga']}")
        print(f"  Taxa de Colisões: {estatisticas['taxa_colisoes']}%")
        print(f"  Taxa de Overflows: {estatisticas['taxa_overflows']}%")
        
        # Análise de qualidade
        if estatisticas['taxa_colisoes'] < 85:
            print("  TAXA DE COLISÕES: Boa")
        else:
            print("  TAXA DE COLISÕES: Ainda alta - considere reduzir FR ainda mais")
            
        if estatisticas['taxa_overflows'] < 10:
            print("  TAXA DE OVERFLOWS: Excelente")
        else:
            print("  TAXA DE OVERFLOWS: Moderada")
        print("-" * 50)

        # 5. Fazer buscas comparativas
        palavra_a_buscar = "Apple"
        
        # Busca com Table Scan
        print(f"Buscando '{palavra_a_buscar}' com Table Scan...")
        inicio = time.time()
        resultado_scan, custo_scan = tabela.table_scan(palavra_a_buscar)
        tempo_scan = time.time() - inicio
        print(f"  Tempo: {tempo_scan:.6f}s")
        if resultado_scan:
            print(f"  Encontrado: {resultado_scan}")
            print(f"  Custo: {custo_scan} páginas")
        else:
            print(f"  Não encontrado. Custo: {custo_scan} páginas")
        print("-" * 20)

        # Busca com Índice Hash
        print(f"Buscando '{palavra_a_buscar}' com Índice Hash...")
        inicio = time.time()
        resultado_hash, custo_hash, pag_id = indice_hash.buscar(palavra_a_buscar, tabela)
        tempo_hash = time.time() - inicio
        print(f"  Tempo: {tempo_hash:.6f}s")
        if resultado_hash:
            print(f"  Encontrado: {resultado_hash}")
            print(f"  Página ID: {pag_id}")
            print(f"  Custo: {custo_hash} páginas")
        else:
            print(f"  Não encontrado. Custo: {custo_hash} páginas")
        
        # Comparação de performance
        if resultado_scan and resultado_hash:
            melhoria_tempo = ((tempo_scan - tempo_hash) / tempo_scan) * 100
            melhoria_custo = ((custo_scan - custo_hash) / custo_scan) * 100
            print(f"\nCOMPARAÇÃO:")
            print(f"  Tempo - Hash é {melhoria_tempo:.1f}% {'mais rápido' if melhoria_tempo > 0 else 'mais lento'}")
            print(f"  Custo - Hash usa {melhoria_custo:.1f}% {'menos' if melhoria_custo > 0 else 'mais'} páginas")
        print("-" * 30)