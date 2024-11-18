from flask import Blueprint, request, jsonify
from app.models import Usuario
from app import db
import bcrypt  # Librería para hashing de contraseñas

# Crear el Blueprint
bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

# Crear un nuevo usuario (POST)
@bp.route('/', methods=['POST'])
def add_usuario():
    data = request.get_json()
    
    # Validación de datos
    if not data.get('nombres') or not data.get('correo') or not data.get('contraseña'):
        return jsonify({'message': 'Faltan campos requeridos'}), 400
    
    # Verificar si el correo ya existe
    if Usuario.query.filter_by(correo=data['correo']).first():
        return jsonify({'message': 'El correo ya está registrado'}), 400
    
    # Hashear la contraseña con bcrypt
    hashed_password = bcrypt.hashpw(data['contraseña'].encode('utf-8'), bcrypt.gensalt())

    nuevo_usuario = Usuario(
        nombres=data['nombres'],
        apellido=data['apellido'],
        numero_telefonico=data['numero_telefonico'],
        correo=data['correo'],
        contraseña=hashed_password.decode('utf-8')  # Guardamos el hash como string
    )
    db.session.add(nuevo_usuario)
    db.session.commit()
    
    # Devuelve los datos del usuario creado, incluyendo el id generado automáticamente
    return jsonify({
        'message': 'Usuario agregado con éxito',
        'usuario': {
            'id': nuevo_usuario.id,
            'nombres': nuevo_usuario.nombres,
            'apellido': nuevo_usuario.apellido,
            'numero_telefonico': nuevo_usuario.numero_telefonico,
            'correo': nuevo_usuario.correo
        }
    }), 201


# Leer todos los usuarios (GET)
@bp.route('/', methods=['GET'])
def get_usuarios():
    usuarios = Usuario.query.all()
    output = [
        {
            'id': u.id,
            'nombres': u.nombres,
            'apellido': u.apellido,
            'numero_telefonico': u.numero_telefonico,
            'correo': u.correo
        }
        for u in usuarios
    ]
    return jsonify(output)

# Leer un usuario por ID (GET)
@bp.route('/<int:id>', methods=['GET'])
def get_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        'id': usuario.id,
        'nombres': usuario.nombres,
        'apellido': usuario.apellido,
        'numero_telefonico': usuario.numero_telefonico,
        'correo': usuario.correo
    })

# Actualizar un usuario (PUT)
@bp.route('/<int:id>', methods=['PUT'])
def update_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()

    usuario.nombres = data.get('nombres', usuario.nombres)
    usuario.apellido = data.get('apellido', usuario.apellido)
    usuario.numero_telefonico = data.get('numero_telefonico', usuario.numero_telefonico)
    usuario.correo = data.get('correo', usuario.correo)
    
    # Actualizar la contraseña solo si se proporciona una nueva
    if 'contraseña' in data:
        hashed_password = bcrypt.hashpw(data['contraseña'].encode('utf-8'), bcrypt.gensalt())
        usuario.contraseña = hashed_password.decode('utf-8')
    
    db.session.commit()
    return jsonify({'message': 'Usuario actualizado con éxito'})

# Eliminar un usuario (DELETE)
@bp.route('/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'message': 'Usuario eliminado con éxito'})


# Ruta para iniciar sesión (POST)
@bp.route('/login', methods=['POST'])
def login_usuario():
    data = request.get_json()
    
    # Verificar si el usuario existe
    usuario = Usuario.query.filter_by(correo=data['correo']).first()
    
    if usuario:
        print(f"Usuario encontrado: {usuario.correo}")
        print(f"Contraseña almacenada: {usuario.contraseña}")
        print(f"Contraseña ingresada: {data['contraseña']}")
    
    # Verificar si las contraseñas coinciden (con bcrypt)
    if usuario and bcrypt.checkpw(data['contraseña'].encode('utf-8'), usuario.contraseña.encode('utf-8')):
        print("Contraseña correcta")
        return jsonify({
            'message': 'Usuario logueado con éxito',
            'usuario': {
                'id': usuario.id,
                'nombres': usuario.nombres,
                'apellido': usuario.apellido,
                'numero_telefonico': usuario.numero_telefonico,
                'correo': usuario.correo
            }
        })
    else:
        print("Correo o contraseña incorrectos")
        return jsonify({'message': 'Correo o contraseña incorrectos'}), 401
