from app import create_app
from flask_cors import CORS
import os  # Importar os para manejar variables de entorno

app = create_app()

# Habilitar CORS para todas las rutas
CORS(app)

if __name__ == '__main__':
    # Usar el puerto asignado por Railway, o el puerto 5000 como fallback
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
