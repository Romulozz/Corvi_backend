from flask import Blueprint, request, jsonify
import mercadopago
from ..models import Compra, db

# Configuración del Blueprint para las rutas de pago
pago_bp = Blueprint('pago', __name__)

# Inicializar el SDK de Mercado Pago con el Access Token proporcionado
sdk = mercadopago.SDK("APP_USR-751137091009208-111815-67eba45b960de3b80ef57bd2aff55be5-2106054836")

# Endpoint para crear la preferencia de pago
@pago_bp.route('/create_preference', methods=['POST'])
def create_preference():
    try:
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
                "currency_id": "PEN"
            })

        print("Lista de items para la preferencia:", preference_items)

        # Configuración de la preferencia de pago con esquemas personalizados
        preference_data = {
            "items": preference_items,
            "back_urls": {
                "success": "corviapp://paymentSuccess",
                "failure": "corviapp://paymentFailure",
                "pending": "corviapp://paymentPending"
            },
            "notification_url": "https://corvibackend-production.up.railway.app/api/pago/notificaciones",
            "auto_return": "approved",
            "additional_info": "Compra en CORVI_APP",
            "shipments": {
                "cost": shipping_cost,
                "mode": "not_specified"
            }
        }

        print("Datos de la preferencia antes de enviar a Mercado Pago:", preference_data)

        preference_response = sdk.preference().create(preference_data)
        print("Respuesta de Mercado Pago:", preference_response)

        if preference_response.get("status") != 201:
            raise Exception(f"Error al crear la preferencia: {preference_response}")

        preference = preference_response["response"]

        # Crear un registro preliminar en la base de datos
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

# Endpoint para recibir notificaciones de Mercado Pago
@pago_bp.route('/notificaciones', methods=['POST'])
def recibir_notificaciones():
    try:
        data = request.json
        print("Notificación recibida:", data)

        if "type" in data and data["type"] == "payment":
            payment_id = data.get("data", {}).get("id")
            if not payment_id:
                raise ValueError("El ID del pago no fue proporcionado en la notificación.")

            payment_info = sdk.payment().get(payment_id)
            print("Información del pago:", payment_info)

            if payment_info["status"] == 200:
                payment_data = payment_info["response"]
                status = payment_data.get("status")
                transaction_id = payment_data.get("order", {}).get("id")

                compra = Compra.query.filter_by(transaction_id=transaction_id).first()
                if compra:
                    compra.estado = status
                    db.session.commit()
                    print("Compra actualizada con éxito. Nuevo estado:", status)
                else:
                    print("No se encontró la compra con el ID de transacción:", transaction_id)

        return jsonify({"message": "Notificación procesada con éxito"}), 200

    except Exception as e:
        print("Error al procesar la notificación:", e)
        return jsonify({"error": "Error al procesar la notificación"}), 500
