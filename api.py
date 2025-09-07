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

    indice_hash = Hash(fr=tamanho_bucket_fr)
    indice_hash.construir(tabela)

    return jsonify({"mensagem": "Índice hash construído com sucesso!"}), 200


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


if __name__ == "__main__":
    app.run(debug=True)
