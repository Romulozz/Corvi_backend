# app/routes/disponibilidad.py

from flask import Blueprint, request, jsonify
from app.models import Maquinaria, DisponibilidadCalendario
from app import db

bp = Blueprint('disponibilidad', __name__, url_prefix='/disponibilidad')

@bp.route('/alquilar', methods=['POST'])
def alquilar_maquinaria():
    data = request.get_json()

    # Obtener la maquinaria por su ID
    maquinaria = Maquinaria.query.get_or_404(data['id_maquinaria'])

    # Registrar el nuevo período de alquiler
    nuevo_alquiler = DisponibilidadCalendario(
        id_maquinaria=maquinaria.id_maquinaria,
        fecha_inicio=data['fecha_inicio'],
        fecha_fin=data['fecha_fin'],
    )

    db.session.add(nuevo_alquiler)
    db.session.commit()

    return jsonify({'message': 'Alquiler registrado con éxito'}), 201


@bp.route('/<int:id_maquinaria>/disponible', methods=['GET'])
def consultar_disponibilidad(id_maquinaria):
    maquinaria = Maquinaria.query.get_or_404(id_maquinaria)

    # Solo verificar si la maquinaria existe
    return jsonify({'message': 'Consulta realizada'}), 200


@bp.route('/cancelar/<int:id_disponibilidad>', methods=['DELETE'])
def cancelar_alquiler(id_disponibilidad):
    alquiler = DisponibilidadCalendario.query.get_or_404(id_disponibilidad)

    db.session.delete(alquiler)
    db.session.commit()

    return jsonify({'message': 'El alquiler ha sido cancelado con éxito'}), 200
