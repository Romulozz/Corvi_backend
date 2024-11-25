from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos usando variable de entorno
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://root:wveAFaCpNabpgjwAaWLgbLBelKuYKoHq@mysql.railway.internal:3306/railway'
    )

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Registrar blueprints
    from .routes import repuestos, maquinaria, disponibilidad, ruc, usuarios, pago, tracking , tokenemail, mercadoPago # Añadimos ruc
    app.register_blueprint(repuestos.bp)
    app.register_blueprint(maquinaria.bp)
    app.register_blueprint(disponibilidad.bp)
    app.register_blueprint(ruc.ruc_bp)  # Registramos el blueprint de ruc
    app.register_blueprint(usuarios.bp)  # Registramos el blueprint de ruc
    app.register_blueprint(pago.pago_bp, url_prefix='/api/pago')  # Registrar el blueprint de pago
    app.register_blueprint(tracking.tracking_bp, url_prefix='/tracking')
    app.register_blueprint(tokenemail.bp)
    app.register_blueprint(mercadoPago.bp)


    with app.app_context():
        db.create_all()

    return app
