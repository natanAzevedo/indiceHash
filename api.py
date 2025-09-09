from flask import Flask, request, jsonify
import time

from obj.hash import Hash
from obj.table import Table
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # libera para todas as origens

# Variáveis globais para armazenar o estado (tabela e índice)
tabela = None
indice_hash = None
NOME_ARQUIVO = "words.txt"


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


# Rota para carregar os dados na tabela
@app.route("/load_data", methods=["POST"])
def load_data():
    global tabela
    data = request.json
    tamanho_pagina = data.get("tamanho_pagina", 100)  # Valor default: 100

    tabela = Table(NOME_ARQUIVO)
    tabela.carregar(tam_pagina=tamanho_pagina)

    if tabela.get_total_tuplas() > 0:
        response = {
            "mensagem": f"Arquivo '{NOME_ARQUIVO}' carregado com sucesso!",
            "total_tuplas": tabela.get_total_tuplas(),
            "total_paginas": tabela.get_total_pag()
        }
        return jsonify(response), 200
    else:
        return jsonify({"erro": "Falha ao carregar o arquivo."}), 500


# Rota para construir o índice hash
@app.route("/build_index", methods=["POST"])
def build_index():
    global tabela, indice_hash
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400

    data = request.json
    tamanho_bucket_fr = data.get("tamanho_bucket_fr", 50)  # Valor default: 50
    metodo_colisao = data.get("metodo_colisao", "overflow")  # Valor default: overflow

    indice_hash = Hash(fr=tamanho_bucket_fr, metodo_colisao=metodo_colisao)
    indice_hash.construir(tabela)

    return jsonify({
        "mensagem": f"Índice hash construído com sucesso usando {metodo_colisao}!",
        "metodo_colisao": metodo_colisao
    }), 200


# Rota para obter estatísticas do índice
@app.route("/statistics", methods=["GET"])
def get_statistics():
    global indice_hash
    if indice_hash is None:
        return jsonify({"erro": "Índice não construído. Construa o índice primeiro."}), 400

    estatisticas = indice_hash.get_estatisticas()
    return jsonify(estatisticas), 200


# Nova rota para obter dados das páginas (para visualização real)
@app.route("/pages", methods=["GET"])
def get_pages():
    global tabela
    if tabela is None:
        return jsonify({"erro": "Tabela não carregada."}), 400

    # Assumindo que Table tem um método get_paginas() que retorna lista de páginas com tuplas
    pages = tabela.get_paginas()  # Ajuste conforme implementação real
    serialized_pages = [
        {"id": i, "tuplas": [t.chave for t in page.tuplas]} for i, page in enumerate(pages)
    ]
    return jsonify(serialized_pages), 200


# Nova rota para obter dados dos buckets (para visualização real)
@app.route("/buckets", methods=["GET"])
def get_buckets():
    global indice_hash
    if indice_hash is None:
        return jsonify({"erro": "Índice não construído."}), 400

    # Assumindo que Hash tem um método get_buckets() que retorna lista de buckets com mapeamentos
    buckets = indice_hash.get_buckets()  # Ajuste conforme implementação real
    serialized_buckets = [
        {"id": i, "entradas": len(bucket.entradas), "overflow": bucket.overflow} for i, bucket in enumerate(buckets)
    ]
    return jsonify(serialized_buckets), 200


# Rota para busca com Table Scan (agora retorna registros escaneados)
@app.route("/search_scan/<palavra>", methods=["GET"])
def search_scan(palavra):
    global tabela
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400

    # Pega parâmetro opcional para limite de registros
    max_records = request.args.get('max_records', 100, type=int)

    inicio = time.time()
    resultado_scan, custo_scan, scan_info = tabela.table_scan_detailed(palavra, max_records)
    fim = time.time()

    resultado_serializado = None
    if resultado_scan:
        resultado_serializado = {
            "chave": resultado_scan.chave,
            "dados": resultado_scan.valor
        }

    response = {
        "tempo_busca": f"{fim - inicio:.6f} segundos",
        "encontrado": resultado_scan is not None,
        "resultado": resultado_serializado,
        "custo": custo_scan,
        "scanned_records": scan_info["records"],
        "total_scanned": scan_info["total_scanned"],
        "limited_view": scan_info["limited"]
    }
    return jsonify(response), 200


# Rota para busca com Índice Hash
@app.route("/search_hash/<palavra>", methods=["GET"])
def search_hash(palavra):
    global tabela, indice_hash
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400
    if indice_hash is None:
        return jsonify({"erro": "Índice não construído. Construa o índice primeiro."}), 400

    inicio = time.time()
    resultado_hash, custo_hash, pag_id = indice_hash.buscar(palavra, tabela)
    fim = time.time()

    resultado_serializado = None
    if resultado_hash:
        resultado_serializado = {
            "chave": resultado_hash.chave,
            "dados": resultado_hash.valor
        }

    response = {
        "tempo_busca": f"{fim - inicio:.6f} segundos",
        "encontrado": resultado_hash is not None,
        "resultado": resultado_serializado,
        "pagina_id": pag_id,
        "custo": custo_hash
    }
    return jsonify(response), 200


# Nova rota para testar diferentes métodos de colisão
@app.route("/test_collision_methods", methods=["POST"])
def test_collision_methods():
    global tabela
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400

    data = request.json
    fr = data.get("fr", 3)  # Valor default: 3

    try:
        resultados = Hash.testar_metodos_colisao(tabela, fr)

        # Preparar resposta comparativa
        comparacao = {}
        for metodo, stats in resultados.items():
            comparacao[metodo] = {
                "total_colisoes": stats["total_colisoes"],
                "taxa_colisoes": stats["taxa_colisoes"],
                "total_overflows": stats["total_overflows"],
                "taxa_overflows": stats["taxa_overflows"],
                "fator_carga": stats["fator_carga"],
                "buckets_vazios": stats["distribuicao"]["buckets_vazios"],
                "buckets_com_overflow": stats["distribuicao"]["buckets_com_overflow"]
            }

        # Determinar o melhor método
        melhor_metodo = min(comparacao.keys(),
                           key=lambda m: comparacao[m]["taxa_colisoes"])

        response = {
            "mensagem": "Teste de métodos de colisão realizado com sucesso!",
            "fr_testado": fr,
            "resultados": comparacao,
            "melhor_metodo": melhor_metodo,
            "resumo": {
                "menor_taxa_colisoes": comparacao[melhor_metodo]["taxa_colisoes"],
                "metodos_testados": list(comparacao.keys())
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao testar métodos: {str(e)}"}), 500


# Nova rota para comparar funções hash
@app.route("/compare_hash_functions", methods=["POST"])
def compare_hash_functions():
    global tabela, indice_hash
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400
    if indice_hash is None:
        return jsonify({"erro": "Índice não construído. Construa o índice primeiro."}), 400

    try:
        resultados = indice_hash.comparar_funcoes_hash(tabela)

        if resultados is None:
            return jsonify({"erro": "Não foi possível comparar as funções hash."}), 400

        # Determinar a melhor função hash
        melhor_funcao = min(resultados.keys(),
                           key=lambda f: resultados[f]["colisoes_teoricas"])

        response = {
            "mensagem": "Comparação de funções hash realizada com sucesso!",
            "resultados": resultados,
            "melhor_funcao": melhor_funcao,
            "resumo": {
                "menor_colisoes": resultados[melhor_funcao]["colisoes_teoricas"],
                "funcoes_testadas": list(resultados.keys())
            }
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"erro": f"Erro ao comparar funções hash: {str(e)}"}), 500


# Nova rota para análise completa de performance
@app.route("/performance_analysis", methods=["POST"])
def performance_analysis():
    global tabela
    if tabela is None or tabela.get_total_tuplas() == 0:
        return jsonify({"erro": "Tabela não carregada. Carregue os dados primeiro."}), 400

    data = request.json
    fr_values = data.get("fr_values", [3, 5, 10])  # Diferentes valores de FR para testar
    palavras_teste = data.get("palavras_teste", ["test", "example", "word"])  # Palavras para busca

    try:
        analise_completa = {}

        for fr in fr_values:
            analise_completa[f"fr_{fr}"] = {}

            # Testar cada método de colisão
            metodos = ['overflow', 'linear_probing', 'quadratic_probing']
            for metodo in metodos:
                # Construir índice com método específico
                hash_temp = Hash(fr=fr, metodo_colisao=metodo)
                hash_temp.construir(tabela)

                # Obter estatísticas
                stats = hash_temp.get_estatisticas()

                # Testar busca
                tempos_busca = []
                custos_busca = []

                for palavra in palavras_teste:
                    inicio = time.time()
                    _, custo, _ = hash_temp.buscar(palavra, tabela)
                    fim = time.time()

                    tempos_busca.append(fim - inicio)
                    custos_busca.append(custo)

                # Calcular médias
                tempo_medio = sum(tempos_busca) / len(tempos_busca) if tempos_busca else 0
                custo_medio = sum(custos_busca) / len(custos_busca) if custos_busca else 0

                analise_completa[f"fr_{fr}"][metodo] = {
                    "estatisticas": stats,
                    "performance_busca": {
                        "tempo_medio": round(tempo_medio * 1000, 4),  # em milissegundos
                        "custo_medio": round(custo_medio, 2),
                        "palavras_testadas": len(palavras_teste)
                    }
                }

        # Encontrar configuração ótima
        melhor_config = None
        menor_tempo = float('inf')

        for fr_key, metodos in analise_completa.items():
            for metodo, dados in metodos.items():
                tempo = dados["performance_busca"]["tempo_medio"]
                if tempo < menor_tempo:
                    menor_tempo = tempo
                    melhor_config = f"{fr_key}_{metodo}"

        response = {
            "mensagem": "Análise de performance completada!",
            "analise_completa": analise_completa,
            "melhor_configuracao": melhor_config,
            "fr_testados": fr_values,
            "palavras_teste": palavras_teste
        }

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"erro": f"Erro na análise de performance: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
