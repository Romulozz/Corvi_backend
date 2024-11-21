import random
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from app import db
from app.models import Usuario, Token
import smtplib

# Credenciales de correo
EMAIL_USER = "lester.samuel.cordova.vivas@gmail.com"
EMAIL_PASSWORD = "tzkq dxti wnfx byxo"

# Crear el Blueprint
bp = Blueprint('tokens', __name__, url_prefix='/tokens')

# Generar y enviar el token
@bp.route('/generate', methods=['POST'])
def generate_token():
    data = request.get_json()

    # Verificar si el usuario existe
    usuario_id = data.get('usuario_id')
    if not usuario_id:
        return jsonify({'message': 'Usuario no identificado'}), 400

    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({'message': 'Usuario no encontrado'}), 404

    # Generar un token de 6 dígitos
    token_value = random.randint(100000, 999999)
    expiration_time = datetime.utcnow() + timedelta(minutes=10)

    # Guardar el token en la base de datos
    nuevo_token = Token(usuario_id=usuario.id, token=str(token_value), expires_at=expiration_time)
    db.session.add(nuevo_token)
    db.session.commit()

    # Enviar el token al correo del usuario
    try:
        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(EMAIL_USER, EMAIL_PASSWORD)
        subject = "Tu token de validación"
        body = f"Tu token es: {token_value}. Este código expira en 10 minutos."
        message = f"Subject: {subject}\n\n{body}"
        smtp.sendmail(EMAIL_USER, usuario.correo, message.encode('utf-8'))
        smtp.quit()
        return jsonify({'message': 'Token enviado al correo'})
    except Exception as e:
        return jsonify({'message': f'Error al enviar el correo: {str(e)}'}), 500

# Validar el token
@bp.route('/validate', methods=['POST'])
def validate_token():
    data = request.get_json()

    # Obtener datos del request
    usuario_id = data.get('usuario_id')
    token_value = data.get('token')

    if not usuario_id or not token_value:
        return jsonify({'message': 'Faltan datos para validar el token'}), 400

    # Buscar el token en la base de datos
    token_data = Token.query.filter_by(usuario_id=usuario_id, token=token_value).first()

    if not token_data:
        return jsonify({'message': 'Token inválido o no encontrado'}), 404

    # Verificar si el token ha expirado
    if datetime.utcnow() > token_data.expires_at:
        return jsonify({'message': 'Token expirado'}), 400

    # Token válido
    return jsonify({'message': 'Token válido. Contrato firmado con éxito'})
