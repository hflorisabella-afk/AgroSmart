# inventario.py
# Este archivo define qué es un "ItemInventario" dentro de AgroSmart.
# Sirve para semillas, fertilizantes o herramientas.

class ItemInventario:
    def __init__(self, codigo, nombre, tipo, cantidad, unidad, cantidad_minima):
        self.codigo = codigo                  # código único, ej: "INV001"
        self.nombre = nombre                  # ej: "Semilla de maíz"
        self.tipo = tipo                      # ej: "Semilla", "Fertilizante", "Herramienta"
        self.cantidad = cantidad              # ej: 15
        self.unidad = unidad                  # ej: "kg", "litros", "unidades"
        self.cantidad_minima = cantidad_minima  # a partir de qué cantidad se considera "bajo"

    def esta_bajo(self):
        # Esta función dice si hay que mandar una alerta de inventario bajo
        return self.cantidad <= self.cantidad_minima

    def __str__(self):
        estado = "⚠️ BAJO" if self.esta_bajo() else "OK"
        return f"[{self.codigo}] {self.nombre}: {self.cantidad} {self.unidad} ({estado})"


# --- Zona de prueba ---
if __name__ == "__main__":
    item1 = ItemInventario(t
        codigo="INV001",
        nombre="Semilla de maíz",
        tipo="Semilla",
        cantidad=3,
        unidad="kg",
        cantidad_minima=5
    )

    print(item1)