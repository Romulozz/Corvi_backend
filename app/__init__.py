# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/corvi_bd'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Registrar blueprints
    from .routes import repuestos, maquinaria, disponibilidad  # Añadir el blueprint de disponibilidad
    app.register_blueprint(repuestos.bp)
    app.register_blueprint(maquinaria.bp)
    app.register_blueprint(disponibilidad.bp)  # Registro del nuevo blueprint

    with app.app_context():
        db.create_all()

    return app
