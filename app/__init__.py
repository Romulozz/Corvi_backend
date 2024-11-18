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
    from .routes import repuestos, maquinaria, disponibilidad, ruc, usuarios, pago  # Añadimos ruc
    app.register_blueprint(repuestos.bp)
    app.register_blueprint(maquinaria.bp)
    app.register_blueprint(disponibilidad.bp)
    app.register_blueprint(ruc.ruc_bp)  # Registramos el blueprint de ruc
    app.register_blueprint(usuarios.bp)  # Registramos el blueprint de ruc
    app.register_blueprint(pago.pago_bp, url_prefix='/api/pago')  # Registrar el blueprint de pago

    with app.app_context():
        db.create_all()

    return app
