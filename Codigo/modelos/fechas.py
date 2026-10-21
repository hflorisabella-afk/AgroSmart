# fechas.py
# Funciones para que las fechas siempre se guarden como AAAA-MM-DD (con ceros),
# por ejemplo 2026-09-08 y no 2026-09-8. Así se ordenan bien.

from datetime import datetime


def normalizar_fecha(texto):
    # Valida la fecha y la devuelve con ceros. Si es inválida, lanza ValueError.
    return datetime.strptime(str(texto).strip(), "%Y-%m-%d").strftime("%Y-%m-%d")


def normalizar_fecha_segura(texto):
    # Igual que la anterior, pero si la fecha es inválida devuelve el texto tal cual.
    try:
        return normalizar_fecha(texto)
    except ValueError:
        return texto