import random

def generate_tracking_code():
    """Genera un código de rastreo realista para Perú."""
    prefix = random.choice(['RX', 'LX', 'EX'])  # RX: estándar, LX: internacional, EX: expreso
    number = ''.join(random.choices('0123456789', k=9))  # Número único de 9 dígitos
    suffix = 'PE'  # Indica Perú como país de origen
    return f"{prefix}{number}{suffix}"

    