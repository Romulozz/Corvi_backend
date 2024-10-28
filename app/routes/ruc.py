from flask import Blueprint, jsonify, request
import requests
from app import db

ruc_bp = Blueprint('ruc', __name__)

TOKEN = 'apis-token-10713.PAAkKb3ZBpvqWHrYW1JtyNDeS1pfW36Y'

# Ruta para consulta parcial de RUC
@ruc_bp.route('/ruc/parcial/<ruc>', methods=['GET']) 
def consulta_parcial_ruc(ruc):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }
    url = f'https://api.apis.net.pe/v2/sunat/ruc'
    params = {'numero': ruc}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Ruta para consulta extendida de RUC
@ruc_bp.route('/ruc/extendida/<ruc>', methods=['GET'])
def consulta_extendida_ruc(ruc):
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {TOKEN}'
    }
    url = f'https://api.apis.net.pe/v2/sunat/ruc/full'
    params = {'numero': ruc}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        return jsonify({'error': str(e)}), 500
