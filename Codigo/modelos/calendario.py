# calendario.py
from datetime import datetime, timedelta

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


class GestorCalendario:
    """
    Clase para administrar los eventos y calcular automáticamente
    las predicciones de cosecha según las fechas de siembra.
    """
    def __init__(self):
        self.eventos = []
        # Tiempos promedio de ciclo vegetativo (en días) según tipo de cultivo
        self.dias_maduracion = {
            "maiz": 120,
            "frijol": 75,
            "tomate": 90,
            "cafe": 270,
            "papa": 110
        }

    def agregar_evento(self, evento: EventoCalendario):
        self.eventos.append(evento)

    def calcular_prediccion(self, codigo_cultivo, nombre_cultivo, fecha_siembra_str):
        """
        Calcula la fecha de cosecha proyectada y devuelve una instancia de PrediccionCosecha.
        Formato de fecha_siembra_str: 'YYYY-MM-DD'
        """
        key_cultivo = nombre_cultivo.lower().strip()
        dias_ciclo = self.dias_maduracion.get(key_cultivo, 90)  # 90 días por defecto si no está en dict

        try:
            fecha_siembra = datetime.strptime(fecha_siembra_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("El formato de fecha debe ser YYYY-MM-DD")

        fecha_estimada_obj = fecha_siembra + timedelta(days=dias_ciclo)
        hoy = datetime.now()
        dias_restantes = (fecha_estimada_obj - hoy).days

        # Determinación automática del estado
        if dias_restantes > 15:
            estado = "En crecimiento"
        elif 0 <= dias_restantes <= 15:
            estado = "Próximo a cosechar"
        else:
            estado = "Listo para cosecha (o finalizado)"

        fecha_estimada_str = fecha_estimada_obj.strftime("%Y-%m-%d")

        # Se retorna una nueva instancia de tu clase PrediccionCosecha
        return PrediccionCosecha(
            codigo_cultivo=codigo_cultivo,
            fecha_estimada=fecha_estimada_str,
            dias_restantes=max(0, dias_restantes),
            estado=estado
        )

    def mostrar_calendario(self):
        """Muestra la lista completa de eventos agendados."""
        if not self.eventos:
            print("No hay eventos registrados en el calendario.")
            return

        print("\n--- AGENDA DE EVENTOS AGRÍCOLAS ---")
        for ev in sorted(self.eventos, key=lambda x: x.fecha):
            print(ev)


# --- Zona de prueba ---
if __name__ == "__main__":
    gestor = GestorCalendario()

    # 1. Pruebas de tus instancias originales
    evento1 = EventoCalendario(
        codigo="EVT001",
        codigo_cultivo="CULT001",
        tipo="Fertilización",
        fecha="2026-09-01",
        descripcion="Aplicar fertilizante NPK"
    )
    gestor.agregar_evento(evento1)

    gestor.agregar_evento(EventoCalendario("EVT002", "CULT001", "Riego", "2026-09-20", "Riego por goteo programado"))

    # Mostrar agenda
    gestor.mostrar_calendario()

    print("\n--- PREDICCIÓN DE COSECHAS ---")

    # 2. Generación dinámica de predicciones por fecha de siembra
    pred1 = gestor.calcular_prediccion(
        codigo_cultivo="CULT001",
        nombre_cultivo="maiz",
        fecha_siembra_str="2026-07-01"
    )
    print(pred1)

    pred2 = gestor.calcular_prediccion(
        codigo_cultivo="CULT002",
        nombre_cultivo="frijol",
        fecha_siembra_str="2026-08-15"
    )
    print(pred2)