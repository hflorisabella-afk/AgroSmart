# riego.py
# Este archivo define qué es un "Riego" dentro de AgroSmart.
# Cada vez que alguien riegue un cultivo, se crea uno de estos para llevar el historial.

class Riego:
    def __init__(self, codigo, codigo_cultivo, fecha, cantidad_agua, observacion=""):
        self.codigo = codigo                      # código único del riego, ej: "RIEGO001"
        self.codigo_cultivo = codigo_cultivo       # a qué cultivo se le regó (usa el codigo de Cultivo)
        self.fecha = fecha                         # ej: "2026-08-19"
        self.cantidad_agua = cantidad_agua         # ej: 20 (en litros)
        self.observacion = observacion             # ej: "Riego por altas temperaturas"

    def __str__(self):
        return f"[{self.codigo}] Cultivo {self.codigo_cultivo} - {self.cantidad_agua}L el {self.fecha}"


# --- Zona de prueba ---
if __name__ == "__main__":
    riego1 = Riego(
        codigo="RIEGO001",
        codigo_cultivo="CULT001",
        fecha="2026-08-19",
        cantidad_agua=20,
        observacion="Riego por altas temperaturas"
    )

    print(riego1)