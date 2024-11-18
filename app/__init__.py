from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Inicializar la instancia de SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:26112004@localhost/corvi'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Inicializar SQLAlchemy con la aplicación
    db.init_app(app)

    # Registrar blueprints
    from .routes import repuestos, maquinaria, disponibilidad, ruc, pago, paypal  # Añadir "pago"
    app.register_blueprint(repuestos.bp)
    app.register_blueprint(maquinaria.bp)
    app.register_blueprint(disponibilidad.bp)
    app.register_blueprint(ruc.ruc_bp)
    app.register_blueprint(pago.pago_bp, url_prefix='/api/pago')  # Registrar el blueprint de pago
    app.register_blueprint(paypal.bp, url_prefix="/api/paypal")

    # Crear todas las tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    return app
