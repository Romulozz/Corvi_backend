# app/routes/disponibilidad.py

from flask import Blueprint, request, jsonify
from app.models import Maquinaria, DisponibilidadCalendario
from app import db
from datetime import datetime

# Crear el Blueprint
bp = Blueprint('disponibilidad', __name__, url_prefix='/disponibilidad')

# Ruta para añadir un nuevo período de disponibilidad o alquiler (POST)
@bp.route('/alquilar', methods=['POST'])
def alquilar_maquinaria():
    data = request.get_json()

    # Obtener la maquinaria
    maquinaria = Maquinaria.query.get_or_404(data['id_maquinaria'])

    # Verificar que la maquinaria esté disponible en general (campo `disponibilidad` en Maquinaria)
    if not maquinaria.disponibilidad:
        return jsonify({'message': 'La maquinaria no está disponible para alquilar'}), 400

    # Obtener las fechas de alquiler
    fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d %H:%M:%S')
    fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d %H:%M:%S')

    # Verificar si ya está alquilada en ese período
    conflictos = DisponibilidadCalendario.query.filter(
        DisponibilidadCalendario.id_maquinaria == maquinaria.id_maquinaria,
        DisponibilidadCalendario.fecha_inicio < fecha_fin,
        DisponibilidadCalendario.fecha_fin > fecha_inicio
    ).all()

    if conflictos:
        return jsonify({'message': 'La maquinaria ya está alquilada en las fechas solicitadas'}), 400

    # Si no hay conflictos, registrar el nuevo período de alquiler
    nuevo_alquiler = DisponibilidadCalendario(
        id_maquinaria=maquinaria.id_maquinaria,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado='alquilada'  # Se guarda como "alquilada"
    )

    db.session.add(nuevo_alquiler)
    db.session.commit()

    return jsonify({'message': 'Alquiler registrado con éxito'}), 201

# Ruta para consultar disponibilidad de maquinaria (GET)
@bp.route('/<int:id_maquinaria>/disponible', methods=['GET'])
def consultar_disponibilidad(id_maquinaria):
    maquinaria = Maquinaria.query.get_or_404(id_maquinaria)

    # Obtener las fechas de inicio y fin que queremos consultar
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')

    if fecha_inicio and fecha_fin:
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')

        # Consultar la disponibilidad en esas fechas
        conflictos = DisponibilidadCalendario.query.filter(
            DisponibilidadCalendario.id_maquinaria == maquinaria.id_maquinaria,
            DisponibilidadCalendario.fecha_inicio < fecha_fin,
            DisponibilidadCalendario.fecha_fin > fecha_inicio
        ).all()

        if conflictos:
            return jsonify({'message': 'La maquinaria está alquilada en las fechas solicitadas'}), 400
        else:
            return jsonify({'message': 'La maquinaria está disponible en las fechas solicitadas'}), 200

    return jsonify({'message': 'Por favor, proporciona fecha de inicio y fecha de fin'}), 400

# Ruta para cancelar un período de alquiler (DELETE)
@bp.route('/cancelar/<int:id_disponibilidad>', methods=['DELETE'])
def cancelar_alquiler(id_disponibilidad):
    alquiler = DisponibilidadCalendario.query.get_or_404(id_disponibilidad)

    db.session.delete(alquiler)
    db.session.commit()

    return jsonify({'message': 'El alquiler ha sido cancelado con éxito'}), 200
