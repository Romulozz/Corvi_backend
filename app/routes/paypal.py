from flask import Blueprint, request, jsonify
import requests

# Blueprint para los endpoints de PayPal
bp = Blueprint("paypal", __name__)

# Credenciales de PayPal Sandbox
PAYPAL_CLIENT_ID = "AXAW4byVkArhD3Rd1H29VUs-JfLR-PJhUF3hZun9bPK1p4py7A94_ZGCRnZC-QcIyHSAnkLbeh1MoAFV"
PAYPAL_SECRET = "EGEmHFmHF0MuXnGAY7NYjEWZ-YvoYmph_Wh4sktOurSy_7wjC34W2WfD0IsW85E9W8OCWionI10QKV0J"
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"  # Sandbox URL

# Helper: Obtener token de autenticación
def get_paypal_token():
    auth_response = requests.post(
        f"{PAYPAL_API_BASE}/v1/oauth2/token",
        auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
        data={"grant_type": "client_credentials"},
    )
    if auth_response.status_code == 200:
        return auth_response.json().get("access_token")
    else:
        raise Exception("Error al obtener token de PayPal")

# Endpoint: Crear una orden de pago
@bp.route("/create-order", methods=["POST"])
def create_order():
    try:
        token = get_paypal_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        data = request.json
        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "amount": {
                        "currency_code": data.get("currency", "PEN"),  # Moneda en PEN (Soles)
                        "value": data.get("amount", "10.00"),
                    }
                }
            ],
        }
        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders",
            headers=headers,
            json=order_payload,
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Capturar pago
@bp.route("/capture-order/<order_id>", methods=["POST"])
def capture_order(order_id):
    try:
        token = get_paypal_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.post(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}/capture",
            headers=headers,
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint: Consultar el estado de una orden
@bp.route("/get-order/<order_id>", methods=["GET"])
def get_order(order_id):
    try:
        token = get_paypal_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        response = requests.get(
            f"{PAYPAL_API_BASE}/v2/checkout/orders/{order_id}",
            headers=headers,
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
