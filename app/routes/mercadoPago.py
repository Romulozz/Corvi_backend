from flask import Blueprint, request, jsonify
import requests
from app.models import MercadoPagoTransaction
from app import db

# Configuración de Mercado Pago
MERCADO_PAGO_API = "https://api.mercadopago.com"
MERCADO_PAGO_HEADERS = {
    "Authorization": "Bearer TEST-338104734900772-112422-6b70164a8bd865979dd97e9eeba730ff-2105328976"  # Reemplazar con tu token de acceso
}

bp = Blueprint('mercado_pago', __name__, url_prefix='/mercado_pago')

# Obtener tipos de identificación
@bp.route('/identification_types', methods=['GET'])
def get_identification_types():
    try:
        response = requests.get(f"{MERCADO_PAGO_API}/v1/identification_types", headers=MERCADO_PAGO_HEADERS)
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Obtener cuotas
@bp.route('/installments', methods=['GET'])
def get_installments():
    first_six_digits = request.args.get('first_six_digits')
    amount = request.args.get('amount')

    if not first_six_digits or not amount:
        return jsonify({"error": "Faltan parámetros: first_six_digits o amount"}), 400

    try:
        response = requests.get(
            f"{MERCADO_PAGO_API}/v1/payment_methods/installments",
            headers=MERCADO_PAGO_HEADERS,
            params={"bin": first_six_digits, "amount": amount}
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Crear token de tarjeta
@bp.route('/card_token', methods=['POST'])
def create_card_token():
    data = request.get_json()
    try:
        response = requests.post(
            f"{MERCADO_PAGO_API}/v1/card_tokens",
            headers=MERCADO_PAGO_HEADERS,
            json=data
        )
        response.raise_for_status()
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Crear un pago
@bp.route('/payments', methods=['POST'])
def create_payment():
    data = request.get_json()
    try:
        # Guardar detalles del pedido en la base de datos
        transaction = MercadoPagoTransaction(
            transaction_id="PENDING",  # Placeholder hasta recibir respuesta
            status="PENDING",
            transaction_amount=data['transaction_amount'],
            payment_method_id=data['payment_method_id'],
            payer_email=data['payer']['email']
        )
        db.session.add(transaction)
        db.session.commit()

        # Llamar a la API de Mercado Pago
        response = requests.post(
            f"{MERCADO_PAGO_API}/v1/payments",
            headers=MERCADO_PAGO_HEADERS,
            json=data
        )
        response.raise_for_status()
        payment_response = response.json()

        # Actualizar transacción con los datos de Mercado Pago
        transaction.transaction_id = payment_response['id']
        transaction.status = payment_response['status']
        db.session.commit()

        return jsonify(payment_response), response.status_code
    except requests.exceptions.RequestException as e:
        db.session.rollback()  # Revertir si falla la API
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
