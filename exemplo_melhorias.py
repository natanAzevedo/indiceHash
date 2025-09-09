#!/usr/bin/env python3
"""
Exemplo de uso das melhorias implementadas no sistema de índice hash.
Este arquivo demonstra como usar as novas funcionalidades para testar
diferentes métodos de colisão e analisar performance.
"""

from obj.hash import Hash
from obj.table import Table
import time
import json

def exemplo_teste_metodos_colisao():
    """Exemplo baseado no código fornecido pelo usuário"""
    print("=== EXEMPLO: Testando Métodos de Colisão ===")

    # Carregar dados na tabela
    tabela = Table("words.txt")
    tabela.carregar(tam_pagina=5)

    print(f"Tabela carregada: {tabela.get_total_tuplas()} tuplas")

    # Testar diferentes métodos com FR = 3
    resultados = Hash.testar_metodos_colisao(tabela, fr=3)

    # Exibir comparação detalhada
    print("\n=== COMPARAÇÃO DETALHADA ===")
    for metodo, stats in resultados.items():
        print(f"\n{metodo.upper()}:")
        print(f"  - Colisões: {stats['total_colisoes']} ({stats['taxa_colisoes']}%)")
        print(f"  - Overflows: {stats['total_overflows']} ({stats['taxa_overflows']}%)")
        print(f"  - Fator de carga: {stats['fator_carga']}")
        print(f"  - Buckets vazios: {stats['distribuicao']['buckets_vazios']}")
        print(f"  - Buckets com overflow: {stats['distribuicao']['buckets_com_overflow']}")

    return resultados

def exemplo_comparacao_funcoes_hash():
    """Exemplo de comparação de funções hash"""
    print("\n=== EXEMPLO: Comparando Funções Hash ===")

    tabela = Table("words.txt")
    tabela.carregar(tam_pagina=5)

    # Criar índice para testar
    hash_index = Hash(fr=5, metodo_colisao='overflow')
    hash_index.construir(tabela)

    # Comparar funções hash
    resultados = hash_index.comparar_funcoes_hash(tabela)

    print("\nComparação de funções hash:")
    for funcao, dados in resultados.items():
        print(f"\n{funcao.upper()}:")
        print(f"  - Colisões teóricas: {dados['colisoes_teoricas']}")
        print(f"  - Buckets utilizados: {dados['buckets_utilizados']}")
        print(f"  - Máximo por bucket: {dados['max_por_bucket']}")
        print(f"  - Desvio padrão: {dados['desvio_padrao']:.2f}")

    return resultados

def exemplo_analise_performance():
    """Exemplo de análise completa de performance"""
    print("\n=== EXEMPLO: Análise de Performance ===")

    tabela = Table("words.txt")
    tabela.carregar(tam_pagina=10)

    # Diferentes configurações para testar
    fr_values = [3, 5, 10]
    metodos = ['overflow', 'linear_probing', 'quadratic_probing']
    palavras_teste = ["the", "and", "test", "example", "word"]

    resultados_performance = {}

    for fr in fr_values:
        print(f"\nTestando FR = {fr}:")
        resultados_performance[fr] = {}

        for metodo in metodos:
            print(f"  Método: {metodo}")

            # Construir índice
            hash_index = Hash(fr=fr, metodo_colisao=metodo)
            hash_index.construir(tabela)

            # Testar performance de busca
            tempos = []
            custos = []

            for palavra in palavras_teste:
                inicio = time.time()
                resultado, custo, _ = hash_index.buscar(palavra, tabela)
                fim = time.time()

                tempos.append(fim - inicio)
                custos.append(custo)

            # Calcular médias
            tempo_medio = sum(tempos) / len(tempos)
            custo_medio = sum(custos) / len(custos)

            resultados_performance[fr][metodo] = {
                'tempo_medio_ms': tempo_medio * 1000,
                'custo_medio': custo_medio,
                'estatisticas': hash_index.get_estatisticas()
            }

            print(f"    Tempo médio: {tempo_medio * 1000:.4f} ms")
            print(f"    Custo médio: {custo_medio:.2f}")
            print(f"    Taxa colisões: {hash_index.get_estatisticas()['taxa_colisoes']}%")

    return resultados_performance

def exemplo_uso_api():
    """Exemplo de como usar as novas rotas da API"""
    print("\n=== EXEMPLO: Uso das Novas Rotas da API ===")

    # Exemplos de requests que podem ser feitos
    exemplos_requests = {
        "Carregar dados": {
            "url": "POST /load_data",
            "body": {"tamanho_pagina": 100}
        },

        "Construir índice com método específico": {
            "url": "POST /build_index",
            "body": {
                "tamanho_bucket_fr": 5,
                "metodo_colisao": "linear_probing"
            }
        },

        "Testar métodos de colisão": {
            "url": "POST /test_collision_methods",
            "body": {"fr": 3}
        },

        "Comparar funções hash": {
            "url": "POST /compare_hash_functions",
            "body": {}
        },

        "Análise completa de performance": {
            "url": "POST /performance_analysis",
            "body": {
                "fr_values": [3, 5, 10],
                "palavras_teste": ["test", "example", "word"]
            }
        }
    }

    print("Rotas disponíveis para teste:")
    for nome, config in exemplos_requests.items():
        print(f"\n{nome}:")
        print(f"  URL: {config['url']}")
        print(f"  Body: {json.dumps(config['body'], indent=4)}")

def main():
    """Função principal que executa todos os exemplos"""
    print("🚀 DEMONSTRAÇÃO DAS MELHORIAS IMPLEMENTADAS")
    print("=" * 50)

    try:
        # Exemplo 1: Teste de métodos de colisão
        resultados_metodos = exemplo_teste_metodos_colisao()

        # Exemplo 2: Comparação de funções hash
        resultados_funcoes = exemplo_comparacao_funcoes_hash()

        # Exemplo 3: Análise de performance
        resultados_performance = exemplo_analise_performance()

        # Exemplo 4: Uso da API
        exemplo_uso_api()

        print("\n" + "=" * 50)
        print("✅ RESUMO DOS RESULTADOS")
        print("=" * 50)

        # Melhor método de colisão
        melhor_metodo = min(resultados_metodos.keys(),
                           key=lambda m: resultados_metodos[m]['taxa_colisoes'])
        print(f"🏆 Melhor método de colisão: {melhor_metodo}")
        print(f"   Taxa de colisões: {resultados_metodos[melhor_metodo]['taxa_colisoes']}%")

        # Melhor função hash
        melhor_funcao = min(resultados_funcoes.keys(),
                           key=lambda f: resultados_funcoes[f]['colisoes_teoricas'])
        print(f"🏆 Melhor função hash: {melhor_funcao}")
        print(f"   Colisões teóricas: {resultados_funcoes[melhor_funcao]['colisoes_teoricas']}")

        print("\n🎯 As melhorias implementadas incluem:")
        print("   ✅ Função para testar métodos de colisão automaticamente")
        print("   ✅ Comparação de diferentes funções hash")
        print("   ✅ Análise completa de performance")
        print("   ✅ Novas rotas na API para testes automatizados")
        print("   ✅ Suporte para seleção de método de colisão na API")

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        print("Verifique se o arquivo 'words.txt' existe no diretório.")

if __name__ == "__main__":
    main()
