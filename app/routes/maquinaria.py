# app/routes/maquinaria.py

from flask import Blueprint, request, jsonify
from app.models import Maquinaria
from app import db
from datetime import datetime

# Crear el Blueprint
bp = Blueprint('maquinaria', __name__, url_prefix='/maquinaria')

# Crear la tabla Maquinaria
@bp.route('/create_table', methods=['GET'])
def create_table():
    db.create_all()  # Esto crea todas las tablas, incluida la tabla Maquinaria
    return jsonify({'message': 'Tabla Maquinaria creada con éxito'}), 200

# Crear (POST)
@bp.route('/', methods=['POST'])
def add_maquinaria():
    data = request.get_json()
    nueva_maquinaria = Maquinaria(
        nombre=data['nombre'],
        tipo=data['tipo'],
        img=data.get('img'),  # Cambiado 'img_demostrativo' a 'img'
        disponibilidad=bool(data['disponibilidad']),  # Asegurarse de que es booleano
        precio=data['precio'],
        estado=data['estado'],
        descripcion=data.get('descripcion'),
        ultimo_mantenimiento=datetime.strptime(data['ultimo_mantenimiento'], '%Y-%m-%d %H:%M:%S')
    )
    db.session.add(nueva_maquinaria)
    db.session.commit()
    return jsonify({'message': 'Maquinaria agregada con éxito'}), 201

# Leer todas las maquinarias (GET)
@bp.route('/', methods=['GET'])
def get_maquinarias():
    maquinarias = Maquinaria.query.all()
    output = [
        {
            'id_maquinaria': m.id_maquinaria,
            'nombre': m.nombre,
            'tipo': m.tipo,
            'img': m.img,  # Cambiado 'img_demostrativo' a 'img'
            'disponibilidad': m.disponibilidad,  # Ahora es booleano
            'precio': float(m.precio),
            'estado': m.estado,
            'descripcion': m.descripcion,
            'ultimo_mantenimiento': m.ultimo_mantenimiento.strftime('%Y-%m-%d %H:%M:%S')
        }
        for m in maquinarias
    ]
    return jsonify(output)

# Leer una maquinaria por ID (GET)
@bp.route('/<int:id>', methods=['GET'])
def get_maquinaria(id):
    maquinaria = Maquinaria.query.get_or_404(id)
    return jsonify({
        'id_maquinaria': maquinaria.id_maquinaria,
        'nombre': maquinaria.nombre,
        'tipo': maquinaria.tipo,
        'img': maquinaria.img,  # Cambiado 'img_demostrativo' a 'img'
        'disponibilidad': maquinaria.disponibilidad,  # Ahora es booleano
        'precio': float(maquinaria.precio),
        'estado': maquinaria.estado,
        'descripcion': maquinaria.descripcion,
        'ultimo_mantenimiento': maquinaria.ultimo_mantenimiento.strftime('%Y-%m-%d %H:%M:%S')
    })

# Actualizar (PUT)
@bp.route('/<int:id>', methods=['PUT'])
def update_maquinaria(id):
    maquinaria = Maquinaria.query.get_or_404(id)
    data = request.get_json()

    maquinaria.nombre = data.get('nombre', maquinaria.nombre)
    maquinaria.tipo = data.get('tipo', maquinaria.tipo)
    maquinaria.img = data.get('img', maquinaria.img)  # Cambiado 'img_demostrativo' a 'img'
    maquinaria.disponibilidad = bool(data.get('disponibilidad', maquinaria.disponibilidad))  # Asegurar que es booleano
    maquinaria.precio = data.get('precio', maquinaria.precio)
    maquinaria.estado = data.get('estado', maquinaria.estado)
    maquinaria.descripcion = data.get('descripcion', maquinaria.descripcion)
    maquinaria.ultimo_mantenimiento = datetime.strptime(
        data.get('ultimo_mantenimiento', maquinaria.ultimo_mantenimiento.strftime('%Y-%m-%d %H:%M:%S')),
        '%Y-%m-%d %H:%M:%S'
    )

    db.session.commit()
    return jsonify({'message': 'Maquinaria actualizada con éxito'})

# Eliminar (DELETE)
@bp.route('/<int:id>', methods=['DELETE'])
def delete_maquinaria(id):
    maquinaria = Maquinaria.query.get_or_404(id)
    db.session.delete(maquinaria)
    db.session.commit()
    return jsonify({'message': 'Maquinaria eliminada con éxito'})
