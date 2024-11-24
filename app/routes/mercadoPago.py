from flask import Blueprint, request, jsonify
import requests
from app.models import CompraMercado, db
from datetime import datetime

api_mercado = Blueprint('api_mercado', __name__, url_prefix='/api/mercado')

# Configuración de Mercado Pago
MERCADO_PAGO_API = "https://api.mercadopago.com"
HEADERS = {
    "Authorization": "Bearer TEST-6552345955475426-112201-0488bdeeb94be7204d9f4f55fc5f5431-654523713"
}

@api_mercado.route('/identification_types', methods=['GET'])
def get_identification_types():
    try:
        response = requests.get(f"{MERCADO_PAGO_API}/v1/identification_types", headers=HEADERS)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400

@api_mercado.route('/installments/<string:first_six_digits>/<float:amount>', methods=['GET'])
def get_installments(first_six_digits, amount):
    try:
        params = {"bin": first_six_digits, "amount": amount}
        response = requests.get(f"{MERCADO_PAGO_API}/v1/payment_methods/installments", headers=HEADERS, params=params)
        response.raise_for_status()
        return jsonify(response.json()), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400

@api_mercado.route('/card_token', methods=['POST'])
def create_card_token():
    data = request.get_json()
    try:
        response = requests.post(f"{MERCADO_PAGO_API}/v1/card_tokens", headers=HEADERS, json=data)
        response.raise_for_status()
        return jsonify(response.json()), 201
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 400

@api_mercado.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    try:
        # Crear una nueva transacción en la base de datos
        new_compra = CompraMercado(
            transaction_id=None,  # Se actualizará después del pago
            monto=data['transaction_amount'],
            estado='pending',
            detalles=data.get('order', {})
        )
        db.session.add(new_compra)
        db.session.commit()

        # Enviar el pago a Mercado Pago
        response = requests.post(f"{MERCADO_PAGO_API}/v1/payments", headers=HEADERS, json=data)
        response.raise_for_status()
        payment_response = response.json()

        # Actualizar la compra con el ID de transacción y estado
        new_compra.transaction_id = payment_response['id']
        new_compra.estado = payment_response['status']
        db.session.commit()

        return jsonify(payment_response), 201
    except requests.exceptions.RequestException as e:
        db.session.rollback()  # Revertir cambios en caso de error
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error interno"}), 500