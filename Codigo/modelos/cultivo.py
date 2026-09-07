# cultivo.py
# Este archivo define qué es un "Cultivo" dentro de AgroSmart.
# Aquí NO se hace pantallas ni preguntamos nada al usuario,
# solo definimos la "forma" que va a tener un cultivo en el sistema.

class Cultivo:
    def __init__(self, codigo, nombre, tipo, tipo_tierra, localidad, numero_parcela, tamano_parcela, fecha_siembra, estado="Sembrado"):
        # self = "este cultivo en específico" (cada cultivo que crees será distinto)
        self.codigo = codigo                  # código único, ej: "CULT001" (para la tabla hash)
        self.nombre = nombre                  # ej: "Maíz parcela 3"
        self.tipo = tipo                      # ej: "Maíz", "Frijol", "Café"
        self.tipo_tierra = tipo_tierra        # ej: "Arcillosa", "Arenosa"
        self.localidad = localidad            # ej: "Chimaltenango"
        self.numero_parcela = numero_parcela  # ej: "3" (identifica la parcela dentro de la localidad)
        self.tamano_parcela = tamano_parcela  # ej: 2.5 (en hectáreas)
        self.fecha_siembra = fecha_siembra    # ej: "2026-08-18"
        self.estado = estado                  # ej: "Sembrado", "Creciendo", "Listo para cosecha"

    def __str__(self):
        # Esto es solo para que, al imprimir un cultivo, se vea bonito y no como un objeto raro
        return f"[{self.codigo}] {self.nombre} ({self.tipo}) - Parcela {self.numero_parcela} ({self.tamano_parcela} ha) - {self.estado}"


# --- Zona de prueba ---
if __name__ == "__main__":
    cultivo1 = Cultivo(
        codigo="CULT001",
        nombre="Maíz parcela 3",
        tipo="Maíz",
        tipo_tierra="Arcillosa",
        localidad="Chimaltenango",
        numero_parcela="3",
        tamano_parcela=2.5,
        fecha_siembra="2026-08-18"
    )

    print(cultivo1)