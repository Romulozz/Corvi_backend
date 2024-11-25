from flask import Blueprint, request, jsonify
import mercadopago
from ..models import Compra, db
from datetime import datetime

# Configuración del Blueprint para las rutas de pago
pago_bp = Blueprint('pago', __name__)

# Inicializar el SDK de Mercado Pago con el Access Token proporcionado
sdk = mercadopago.SDK("TEST-338104734900772-112422-6b70164a8bd865979dd97e9eeba730ff-2105328976")

# Endpoint para crear la preferencia de pago
@pago_bp.route('/create_preference', methods=['POST'])
def create_preference():
    try:
        # Imprimir los datos recibidos para depuración
        data = request.get_json()
        print("Datos recibidos en el servidor:", data)

        items = data.get("items", [])
        if not items:
            raise ValueError("La lista de 'items' está vacía o no fue proporcionada.")

        shipping_cost = data.get("shipping_cost", 0)
        print("Costo de envío recibido:", shipping_cost)

        # Crear lista de productos para la preferencia de pago
        preference_items = []
        for item in items:
            print("Procesando item:", item)
            if not all(k in item for k in ("title", "quantity", "unit_price")):
                raise ValueError("Falta una clave en uno de los elementos de 'items'.")

            preference_items.append({
                "title": item["title"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "currency_id": "PEN"  # Configuración para la moneda Sol (PEN)
            })

        print("Lista de items para la preferencia:", preference_items)

        # Configuración de la preferencia de pago
        preference_data = {
            "items": preference_items,
          "back_urls": {
                 "success": "https://mercado-page.web.app/success.html",
                "failure": "https://mercado-page.web.app/failure.html",
                "pending": "https://mercado-page.web.app/pending.html"
            },
            "auto_return": "approved",
            "additional_info": "Compra en CORVI_APP",
            "shipments": {
                "cost": shipping_cost,
                "mode": "not_specified"
            },
            # "notification_url": "http://localhost:5000/api/pago/notifications",  # Comentar esta línea si no es accesible
            # 'payment_methods': {  # Comentar estas líneas si generan conflicto
            #     'excluded_payment_methods': [{'id': ''}], 
            #     'excluded_payment_types': [{'id': ''}],   
            # },
            # 'payer': {  # Comentar estas líneas si hay campos vacíos
            #     'name': '',  
            #     'surname': '',  
            #     'email': '',  
            # },
        }

        print("Datos de la preferencia antes de enviar a Mercado Pago:", preference_data)

        # Crear la preferencia en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        print("Respuesta de Mercado Pago:", preference_response)  # Imprimir la respuesta de Mercado Pago para depuración

        if preference_response.get("status") != 201:
            raise Exception(f"Error al crear la preferencia: {preference_response}")

        preference = preference_response["response"]

        # Guardar un registro preliminar en la base de datos con estado "pending"
        nueva_compra = Compra(
            transaction_id=preference["id"],
            monto=sum(item["unit_price"] * item["quantity"] for item in items) + shipping_cost,
            estado="pending",
            detalles=preference_items
        )
        db.session.add(nueva_compra)
        db.session.commit()

        print("Registro de compra guardado en la base de datos con éxito. ID de transacción:", preference["id"])

        return jsonify({
            "id": preference["id"],
            "init_point": preference["init_point"],
            "total": nueva_compra.monto
        })
    except ValueError as ve:
        print("Error de validación:", ve)
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("Error al crear la preferencia:", e)
        return jsonify({"error": "Error al crear la preferencia"}), 500
