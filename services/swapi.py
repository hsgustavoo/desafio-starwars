# services/swapi.py
import requests

SWAPI_BASE_URL = "https://swapi.dev/api"

def get_swapi_data(endpoint, search=None):
    """
    Busca dados na API do Star Wars.
    endpoint: 'people', 'planets', 'films', etc.
    search: termo para filtrar (opcional).
    """
    url = f"{SWAPI_BASE_URL}/{endpoint}/"
    params = {}
    
    if search:
        params['search'] = search
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Levanta erro se der 404 ou 500
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na SWAPI: {e}")
        return None