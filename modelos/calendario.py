# calendario.py
# Este archivo define dos cosas: un "EventoCalendario" (recordatorios)
# y una "PrediccionCosecha" (para saber cuándo se espera cosechar).

class EventoCalendario:
    def __init__(self, codigo, codigo_cultivo, tipo, fecha, descripcion=""):
        self.codigo = codigo                  # código único, ej: "EVT001"
        self.codigo_cultivo = codigo_cultivo  # a qué cultivo pertenece
        self.tipo = tipo                      # ej: "Riego", "Fertilización", "Cosecha"
        self.fecha = fecha                    # ej: "2026-09-01"
        self.descripcion = descripcion        # ej: "Aplicar fertilizante NPK"

    def __str__(self):
        return f"[{self.codigo}] {self.tipo} - {self.fecha} (Cultivo {self.codigo_cultivo})"


class PrediccionCosecha:
    def __init__(self, codigo_cultivo, fecha_estimada, dias_restantes, estado):
        self.codigo_cultivo = codigo_cultivo      # a qué cultivo pertenece
        self.fecha_estimada = fecha_estimada      # ej: "2026-11-15"
        self.dias_restantes = dias_restantes      # ej: 45
        self.estado = estado                      # ej: "En crecimiento", "Listo para cosecha"

    def __str__(self):
        return f"Cultivo {self.codigo_cultivo}: cosecha estimada {self.fecha_estimada} ({self.dias_restantes} días) - {self.estado}"


# --- Zona de prueba ---
if __name__ == "__main__":
    evento1 = EventoCalendario(
        codigo="EVT001",
        codigo_cultivo="CULT001",
        tipo="Fertilización",
        fecha="2026-09-01",
        descripcion="Aplicar fertilizante NPK"
    )
    print(evento1)

    prediccion1 = PrediccionCosecha(
        codigo_cultivo="CULT001",
        fecha_estimada="2026-11-15",
        dias_restantes=45,
        estado="En crecimiento"
    )
    print(prediccion1)