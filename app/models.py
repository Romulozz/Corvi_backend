from app import db
from datetime import datetime

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

# Modelo Compra para almacenar transacciones de compra
class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), nullable=False)  # ID de la transacción de Mercado Pago
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), nullable=False)  # Estado de la compra (ej. 'approved', 'pending')
    detalles = db.Column(db.JSON, nullable=True)  # Detalles de los productos comprados

    def __init__(self, transaction_id, monto, estado, detalles):
        self.transaction_id = transaction_id
        self.monto = monto
        self.estado = estado
        self.detalles = detalles

    def __repr__(self):
        return f'<Compra {self.id} - Transaction ID: {self.transaction_id}>'
