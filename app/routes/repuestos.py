# app/routes/repuestos.py

from flask import Blueprint, request, jsonify
from app.models import Repuestos
from app import db

# Crear el Blueprint
bp = Blueprint('repuestos', __name__, url_prefix='/repuestos')

# Crear (POST)
@bp.route('/', methods=['POST'])
def add_repuesto():
    data = request.get_json()
    nuevo_repuesto = Repuestos(
        nombre=data['nombre'],
        descripcion=data['descripcion'],
        precio=data['precio'],
        disponibilidad=bool(data['disponibilidad']),  # Asegurarse de que se trata como booleano
        voltaje=data['voltaje'],
        imagen=data.get('imagen')
    )
    db.session.add(nuevo_repuesto)
    db.session.commit()
    return jsonify({'message': 'Repuesto agregado con éxito'}), 201


# Leer todos los repuestos (GET)
@bp.route('/', methods=['GET'])
def get_repuestos():
    repuestos = Repuestos.query.all()
    output = [
        {
            'id_repuestos': r.id_repuestos,
            'nombre': r.nombre,
            'descripcion': r.descripcion,
            'precio': float(r.precio),
            'disponibilidad': r.disponibilidad,
            'voltaje': float(r.voltaje),
            'imagen': r.imagen
        }
        for r in repuestos
    ]
    return jsonify(output)

# Leer un repuesto por ID (GET)
@bp.route('/<int:id>', methods=['GET'])
def get_repuesto(id):
    repuesto = Repuestos.query.get_or_404(id)
    return jsonify({
        'id_repuestos': repuesto.id_repuestos,
        'nombre': repuesto.nombre,
        'descripcion': repuesto.descripcion,
        'precio': repuesto.precio,
        'disponibilidad': repuesto.disponibilidad,
        'voltaje': repuesto.voltaje,
        'imagen': repuesto.imagen
    })

# Actualizar (PUT)
@bp.route('/<int:id>', methods=['PUT'])
def update_repuesto(id):
    repuesto = Repuestos.query.get_or_404(id)
    data = request.get_json()

    repuesto.nombre = data.get('nombre', repuesto.nombre)
    repuesto.descripcion = data.get('descripcion', repuesto.descripcion)
    repuesto.precio = data.get('precio', repuesto.precio)
    repuesto.disponibilidad = data.get('disponibilidad', repuesto.disponibilidad)
    repuesto.voltaje = data.get('voltaje', repuesto.voltaje)
    repuesto.imagen = data.get('imagen', repuesto.imagen)

    db.session.commit()
    return jsonify({'message': 'Repuesto actualizado con éxito'})

# Eliminar (DELETE)
@bp.route('/<int:id>', methods=['DELETE'])
def delete_repuesto(id):
    repuesto = Repuestos.query.get_or_404(id)
    db.session.delete(repuesto)
    db.session.commit()
    return jsonify({'message': 'Repuesto eliminado con éxito'})
