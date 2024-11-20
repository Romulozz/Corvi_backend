from flask import Blueprint, jsonify, request
from app.models import Envio, HistorialEnvio, db  # Importa db directamente desde models
from datetime import datetime

tracking_bp = Blueprint('tracking', __name__)

@tracking_bp.route('/create', methods=['POST'])
def create_tracking():
    """Crear un nuevo envío y generar automáticamente el código de rastreo."""
    data = request.get_json()
    
    # Validar los campos necesarios
    required_fields = ['departamento', 'provincia', 'distrito', 'direccion']
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Campos faltantes: {", ".join(missing_fields)}'}), 400

    try:
        envio = Envio(
            estado='En preparación',
            departamento=data['departamento'],
            provincia=data['provincia'],
            distrito=data['distrito'],
            direccion=data['direccion'],
            fecha_envio=datetime.utcnow()
        )
        db.session.add(envio)
        db.session.commit()
        return jsonify({'message': 'Envío creado con éxito', 'codigo_rastreo': envio.codigo_rastreo}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tracking_bp.route('/<codigo_rastreo>', methods=['GET'])
def get_tracking(codigo_rastreo):
    """Obtener el estado y el historial de un envío."""
    envio = Envio.query.filter_by(codigo_rastreo=codigo_rastreo).first()
    if not envio:
        return jsonify({'error': 'Código de rastreo no encontrado'}), 404

    historial = HistorialEnvio.query.filter_by(id_envio=envio.id_envio).all()
    historial_data = [
        {
            'estado': h.estado,
            'fecha': h.fecha.strftime('%Y-%m-%d %H:%M:%S'),
            'observaciones': h.observaciones
        }
        for h in historial
    ]

    return jsonify({
        'codigo_rastreo': envio.codigo_rastreo,
        'estado_actual': envio.estado,
        'departamento': envio.departamento,
        'provincia': envio.provincia,
        'distrito': envio.distrito,
        'direccion': envio.direccion,
        'fecha_envio': envio.fecha_envio.strftime('%Y-%m-%d %H:%M:%S'),
        'historial': historial_data
    })

@tracking_bp.route('/update', methods=['POST'])
def update_tracking():
    """Actualizar el estado de un envío."""
    data = request.get_json()
    codigo_rastreo = data.get('codigo_rastreo')
    estado = data.get('estado')
    observaciones = data.get('observaciones', '')

    envio = Envio.query.filter_by(codigo_rastreo=codigo_rastreo).first()
    if not envio:
        return jsonify({'error': 'Código de rastreo no encontrado'}), 404

    try:
        envio.estado = estado
        historial = HistorialEnvio(
            id_envio=envio.id_envio,
            estado=estado,
            observaciones=observaciones
        )
        db.session.add(historial)
        db.session.commit()
        return jsonify({'message': 'Estado actualizado con éxito'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
