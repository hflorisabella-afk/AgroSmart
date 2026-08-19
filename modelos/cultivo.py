# Este archivo define qué es un "Cultivo" dentro de AgroSmart.
# Aquí NO hacemos pantallas ni preguntamos nada al usuario,
# solo definimos la "forma" que va a tener un cultivo en el sistema.

class Cultivo:
    def __init__(self, codigo, nombre, tipo, tipo_tierra, localidad, fecha_siembra, estado="Sembrado"):
        # self = "este cultivo en específico" (cada cultivo que crees será distinto)
        self.codigo = codigo                  # código único, ej: "CULT001" (para la tabla hash)
        self.nombre = nombre                  # ej: "Maíz parcela 3"
        self.tipo = tipo                      # ej: "Maíz", "Frijol", "Café"
        self.tipo_tierra = tipo_tierra        # ej: "Arcillosa", "Arenosa"
        self.localidad = localidad            # ej: "Chimaltenango"
        self.fecha_siembra = fecha_siembra    # ej: "2026-08-18"
        self.estado = estado                  # ej: "Sembrado", "Creciendo", "Listo para cosecha"

    def __str__(self):
        # Esto es solo para que, al imprimir un cultivo, se vea bonito y no como un objeto raro
        return f"[{self.codigo}] {self.nombre} ({self.tipo}) - {self.estado}"


# --- Zona de prueba ---
# Este pedazo de abajo solo sirve para comprobar que la clase funciona.
# Cuando ya esté conectado con las pantallas, esto se puede borrar.
if __name__ == "__main__":
    cultivo1 = Cultivo(
        codigo="CULT001",
        nombre="Maíz parcela 3",
        tipo="Maíz",
        tipo_tierra="Arcillosa",
        localidad="Chimaltenango",
        fecha_siembra="2026-08-18"
    )

    print(cultivo1)