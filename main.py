# main.py
import functions_framework
from flask import jsonify
from services.swapi import get_swapi_data

@functions_framework.http
def star_wars_api(request):
    """
    Função Serverless que recebe a requisição HTTP.
    """
    # 1. Habilitar CORS (Para qualquer front-end poder acessar)
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}

    # 2. Ler os parâmetros que o usuário enviou
    # Ex: ?category=people&search=luke&sort=name
    args = request.args
    category = args.get('category')
    search_term = args.get('search')
    sort_by = args.get('sort')

    # Validação básica
    allowed_categories = ['people', 'films', 'starships', 'planets', 'species', 'vehicles']
    if not category or category not in allowed_categories:
        return jsonify({
            "error": "Categoria obrigatória ou inválida.",
            "options": allowed_categories,
            "example": "?category=people&search=luke"
        }), 400, headers

    # 3. Chamar nosso serviço (Separado no passo anterior)
    data = get_swapi_data(category, search_term)

    if not data:
        return jsonify({"error": "Falha ao obter dados da SWAPI"}), 502, headers

    results = data.get('results', [])

    # 4. Lógica de Ordenação (Diferencial do Junior)
    # Se o usuário pediu ?sort=name, a gente ordena a lista
    if sort_by and len(results) > 0:
        # Filmes usam 'title', o resto usa 'name'
        key_check = 'title' if category == 'films' else 'name'
        if key_check in results[0]:
            results = sorted(results, key=lambda x: x[key_check])

    # 5. Resposta Final
    response_data = {
        "message": "Dados recuperados com sucesso",
        "category": category,
        "count": len(results),
        "results": results
    }
    
    return jsonify(response_data), 200, headers