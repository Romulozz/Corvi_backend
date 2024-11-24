from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import string


class Repuestos(db.Model):
    __tablename__ = 'repuestos'
    id_repuestos = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    disponibilidad = db.Column(db.String(50), nullable=False)
    voltaje = db.Column(db.Numeric(10, 2), nullable=False)
    imagen = db.Column(db.String(200), nullable=True)

class Maquinaria(db.Model):
    __tablename__ = 'maquinaria'
    id_maquinaria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    img = db.Column(db.String(200), nullable=True)
    precio_hora = db.Column(db.Numeric(10, 2), nullable=False)  # Precio por hora
    precio_dia = db.Column(db.Numeric(10, 2), nullable=False)   # Precio por día
    descripcion = db.Column(db.Text, nullable=True)
    
    # Nuevo campo estado que solo admite 'disponible' o 'ocupado'
    estado = db.Column(db.Enum('disponible', 'ocupado', name='estado_maquinaria'), nullable=False, default='disponible')

    # Relación uno a muchos con el calendario de disponibilidad
    disponibilidad_calendario = db.relationship('DisponibilidadCalendario', backref='maquinaria', lazy=True)

    def __repr__(self):
        return f'<Maquinaria {self.nombre}>'


class DisponibilidadCalendario(db.Model):
    __tablename__ = 'disponibilidad_calendario'
    id_disponibilidad = db.Column(db.Integer, primary_key=True)
    id_maquinaria = db.Column(db.Integer, db.ForeignKey('maquinaria.id_maquinaria'), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Disponibilidad {self.id_disponibilidad} para Maquinaria {self.id_maquinaria}>'

# Clase Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    # Asegúrate de que el campo id sea autoincrementable
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    numero_telefonico = db.Column(db.String(15), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contraseña = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Usuario {self.nombres} {self.apellido}>'
    
# Modelo Compra para almacenar transacciones de compra
class Compra(db.Model):
    _tablename_ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), nullable=False)  # ID de la transacción de Mercado Pago
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False)  # Estado de la compra (ej. 'approved', 'pending')
    detalles = db.Column(db.JSON, nullable=True)  # Detalles de los productos comprados

    def _init_(self, transaction_id, monto, estado, detalles):
        self.transaction_id = transaction_id
        self.monto = monto
        self.estado = estado
        self.detalles = detalles

    def _repr_(self):
        return f'<Compra {self.id} - Transaction ID: {self.transaction_id}>'

class HistorialEnvio(db.Model):
    __tablename__ = 'historial_envios'
    id_historial = db.Column(db.Integer, primary_key=True)
    id_envio = db.Column(db.Integer, db.ForeignKey('envios.id_envio'), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    observaciones = db.Column(db.Text, nullable=True)

    envio = db.relationship('Envio', backref='historial')

    def __repr__(self):
        return f'<Historial {self.id_historial} - Estado: {self.estado}>'
    
# Función para generar el código de rastreo
def generar_codigo_rastreo():
    """Generar un código único en formato RR123456789PE."""
    prefix = "RR"  # Puedes cambiarlo a otro prefijo
    suffix = "PE"  # Código de país
    digits = ''.join(random.choices(string.digits, k=9))  # 9 dígitos aleatorios
    return f"{prefix}{digits}{suffix}"

class Envio(db.Model):
    __tablename__ = 'envios'
    id_envio = db.Column(db.Integer, primary_key=True)
    codigo_rastreo = db.Column(db.String(100), unique=True, nullable=False, default=generar_codigo_rastreo)
    estado = db.Column(db.String(50), nullable=False, default='En preparación')
    departamento = db.Column(db.String(100), nullable=False)
    provincia = db.Column(db.String(100), nullable=False)
    distrito = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)

class Token(db.Model):
    __tablename__ = 'tokens'  # Nombre de la tabla
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    token = db.Column(db.String(6), nullable=False)  # Token de 6 dígitos
    expires_at = db.Column(db.DateTime, nullable=False)  # Fecha de expiración

    usuario = db.relationship('Usuario', backref=db.backref('tokens', lazy=True))

    def __repr__(self):
        return f'<Token {self.token} para Usuario {self.usuario_id}>'

class CompraMercado(db.Model):
    _tablename_ = 'comprasMercado'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), nullable=True)  # ID de la transacción de Mercado Pago
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False)  # Estados como 'approved', 'pending', 'rejected'
    detalles = db.Column(db.JSON, nullable=True)  # Detalles de la compra, como productos o servicios

    def _init_(self, transaction_id, monto, estado, detalles):
        self.transaction_id = transaction_id
        self.monto = monto
        self.estado = estado
        self.detalles = detalles