import functions_framework
from flask import jsonify
from services.swapi import get_swapi_data

# --- HTML DO FRONTEND (EMBUTIDO PARA FACILITAR) ---
FRONTEND_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Star Wars Explorer | PowerOfData</title>
    <style>
        :root { --yellow: #FFE81F; --black: #111; --gray: #222; }
        body { background-color: var(--black); color: #fff; font-family: 'Arial', sans-serif; margin: 0; padding: 20px; text-align: center; }
        h1 { color: var(--yellow); letter-spacing: 2px; text-transform: uppercase; }
        .container { max-width: 800px; margin: 0 auto; }
        
        /* Controles */
        .controls { background: var(--gray); padding: 20px; border-radius: 10px; border: 1px solid #333; display: flex; gap: 10px; flex-wrap: wrap; justify-content: center; }
        select, input, button { padding: 12px; border-radius: 5px; border: none; font-size: 16px; }
        input { flex-grow: 1; min-width: 200px; }
        button { background-color: var(--yellow); color: var(--black); font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background-color: #d1be15; }

        /* Resultados */
        #results { margin-top: 30px; display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; }
        .card { background: var(--gray); padding: 20px; border-radius: 8px; border: 1px solid #444; text-align: left; box-shadow: 0 4px 6px rgba(0,0,0,0.3); transition: transform 0.2s; }
        .card:hover { transform: translateY(-5px); border-color: var(--yellow); }
        .card h3 { color: var(--yellow); margin-top: 0; }
        .card p { margin: 5px 0; color: #ccc; font-size: 14px; }
        .loading { color: var(--yellow); font-size: 18px; display: none; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Star Wars Explorer</h1>
        <p>Explore a galáxia muito, muito distante...</p>

        <div class="controls">
            <select id="category">
                <option value="people">Personagens</option>
                <option value="films">Filmes</option>
                <option value="starships">Naves</option>
                <option value="planets">Planetas</option>
            </select>
            <input type="text" id="search" placeholder="Ex: Luke, Falcon, Tatooine...">
            <button onclick="searchData()">BUSCAR</button>
        </div>

        <div id="loading" class="loading">Carregando dados da galáxia... 🚀</div>
        <div id="results"></div>
    </div>

    <script>
        async function searchData() {
            const category = document.getElementById('category').value;
            const search = document.getElementById('search').value;
            const resultsDiv = document.getElementById('results');
            const loadingDiv = document.getElementById('loading');

            // Limpa e mostra loading
            resultsDiv.innerHTML = '';
            loadingDiv.style.display = 'block';

            try {
                // Chama a PRÓPRIA API (Backend Python)
                let url = `/?category=${category}`;
                if (search) url += `&search=${search}`;
                if (category === 'people') url += `&sort=name`; // Exemplo de ordenação

                const response = await fetch(url);
                const data = await response.json();

                if (data.error) {
                    resultsDiv.innerHTML = `<p style="color: red">${data.error}</p>`;
                    return;
                }

                if (data.results.length === 0) {
                    resultsDiv.innerHTML = '<p>Nenhum resultado encontrado na Força.</p>';
                    return;
                }

                // Renderiza os Cards
                data.results.forEach(item => {
                    let title = item.name || item.title;
                    let info = '';
                    
                    // Lógica simples para mostrar detalhes diferentes por categoria
                    if (item.birth_year) info += `<p><strong>Nascimento:</strong> ${item.birth_year}</p>`;
                    if (item.gender) info += `<p><strong>Gênero:</strong> ${item.gender}</p>`;
                    if (item.climate) info += `<p><strong>Clima:</strong> ${item.climate}</p>`;
                    if (item.model) info += `<p><strong>Modelo:</strong> ${item.model}</p>`;
                    if (item.director) info += `<p><strong>Diretor:</strong> ${item.director}</p>`;
                    
                    const card = `
                        <div class="card">
                            <h3>${title}</h3>
                            ${info}
                        </div>
                    `;
                    resultsDiv.innerHTML += card;
                });

            } catch (error) {
                resultsDiv.innerHTML = '<p style="color: red">Erro ao conectar com a base rebelde.</p>';
                console.error(error);
            } finally {
                loadingDiv.style.display = 'none';
            }
        }
    </script>
</body>
</html>
"""

@functions_framework.http
def star_wars_api(request):
    """
    Função Híbrida: Retorna Site (HTML) ou Dados (JSON).
    """
    # Configuração de CORS
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {'Access-Control-Allow-Origin': '*'}
    args = request.args
    category = args.get('category')

    # --- LÓGICA NOVA: SE NÃO TEM CATEGORIA, ENTREGA O SITE ---
    if not category:
        return FRONTEND_HTML, 200, headers

    # --- DAQUI PARA BAIXO É O SEU CÓDIGO ANTIGO (BACKEND) ---
    search_term = args.get('search')
    sort_by = args.get('sort')

    allowed_categories = ['people', 'films', 'starships', 'planets', 'species', 'vehicles']
    if category not in allowed_categories:
        return jsonify({
            "error": "Categoria inválida.",
            "options": allowed_categories
        }), 400, headers

    # Busca os dados
    data = get_swapi_data(category, search_term)

    if not data:
        return jsonify({"error": "Falha ao obter dados da SWAPI"}), 502, headers

    results = data.get('results', [])

    # Ordenação
    if sort_by and len(results) > 0:
        key_check = 'title' if category == 'films' else 'name'
        if key_check in results[0]:
            results = sorted(results, key=lambda x: x[key_check])

    return jsonify({
        "message": "Dados recuperados com sucesso",
        "count": len(results),
        "results": results
    }), 200, headers