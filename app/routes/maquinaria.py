# app/routes/maquinaria.py

from flask import Blueprint, request, jsonify
from app.models import Maquinaria
from app import db

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
        img=data.get('img'),  # Este campo es opcional
        precio_hora=data['precio_hora'],  # Nuevo campo
        precio_dia=data['precio_dia'],    # Nuevo campo
        descripcion=data.get('descripcion'),
        estado=data.get('estado', 'disponible')  # Estado, por defecto 'disponible'
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
            'img': m.img,  # Este campo es opcional
            'precio_hora': float(m.precio_hora),  # Nuevo campo
            'precio_dia': float(m.precio_dia),    # Nuevo campo
            'descripcion': m.descripcion,
            'estado': m.estado  # Incluir el estado
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
        'img': maquinaria.img,  # Este campo es opcional
        'precio_hora': float(maquinaria.precio_hora),  # Nuevo campo
        'precio_dia': float(maquinaria.precio_dia),    # Nuevo campo
        'descripcion': maquinaria.descripcion,
        'estado': maquinaria.estado  # Incluir el estado
    })

# Actualizar (PUT)
@bp.route('/<int:id>', methods=['PUT'])
def update_maquinaria(id):
    maquinaria = Maquinaria.query.get_or_404(id)
    data = request.get_json()

    maquinaria.nombre = data.get('nombre', maquinaria.nombre)
    maquinaria.tipo = data.get('tipo', maquinaria.tipo)
    maquinaria.img = data.get('img', maquinaria.img)  # Este campo es opcional
    maquinaria.precio_hora = data.get('precio_hora', maquinaria.precio_hora)  # Nuevo campo
    maquinaria.precio_dia = data.get('precio_dia', maquinaria.precio_dia)    # Nuevo campo
    maquinaria.descripcion = data.get('descripcion', maquinaria.descripcion)
    maquinaria.estado = data.get('estado', maquinaria.estado)  # Actualizar el estado

    db.session.commit()
    return jsonify({'message': 'Maquinaria actualizada con éxito'})

# Eliminar (DELETE)
@bp.route('/<int:id>', methods=['DELETE'])
def delete_maquinaria(id):
    maquinaria = Maquinaria.query.get_or_404(id)
    db.session.delete(maquinaria)
    db.session.commit()
    return jsonify({'message': 'Maquinaria eliminada con éxito'})
