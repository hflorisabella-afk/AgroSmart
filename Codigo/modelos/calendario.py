from datetime import datetime, timedelta
import json
import os
import sys

# Para poder importar el árbol que está en la carpeta estructuras/
sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "estructuras")
)

from arbol_eventos import ArbolEventos
from fechas import normalizar_fecha_segura


class EventoCalendario:

    def __init__(
        self,
        codigo,
        codigo_cultivo,
        tipo,
        fecha,
        descripcion=""
    ):
        self.codigo = codigo
        self.codigo_cultivo = codigo_cultivo
        self.tipo = tipo
        self.fecha = fecha
        self.descripcion = descripcion

    def __str__(self):
        return (
            f"[{self.codigo}] "
            f"{self.tipo} - {self.fecha} "
            f"(Cultivo {self.codigo_cultivo})"
        )


class PrediccionCosecha:

    def __init__(
        self,
        codigo_cultivo,
        fecha_estimada,
        dias_restantes,
        estado
    ):
        self.codigo_cultivo = codigo_cultivo
        self.fecha_estimada = fecha_estimada
        self.dias_restantes = dias_restantes
        self.estado = estado

    def __str__(self):
        return (
            f"Cultivo {self.codigo_cultivo}: "
            f"cosecha estimada {self.fecha_estimada} "
            f"({self.dias_restantes} días) - "
            f"{self.estado}"
        )


class GestorCalendario:

    def __init__(self):

        # Lista de eventos
        self.eventos = []

        # Árbol binario que mantiene los eventos ordenados por fecha
        self.arbol = ArbolEventos()

        # Archivo donde se guardan los eventos
        self.archivo = os.path.join(
            os.path.dirname(__file__),
            "eventos_calendario.json"
        )

        # Días aproximados de maduración
        # según el tipo de cultivo
        self.dias_maduracion = {
            "maiz": 120,
            "maíz": 120,
            "frijol": 75,
            "tomate": 90,
            "cafe": 270,
            "café": 270,
            "papa": 110,
            "arroz": 120,
            "hortalizas": 60
        }

        # Cargar eventos existentes
        self.cargar_datos()

    # =====================================================
    # AGREGAR EVENTO
    # =====================================================

    def agregar_evento(self, evento):

        self.eventos.append(evento)
        self.arbol.insertar(evento)

        self.guardar_datos()

    # =====================================================
    # EVENTOS ORDENADOS (usa el árbol)
    # =====================================================

    def eventos_ordenados(self):

        # Recorrido en orden del árbol:
        # los eventos salen ordenados por fecha
        return self.arbol.en_orden()

    # =====================================================
    # GUARDAR DATOS
    # =====================================================

    def guardar_datos(self):

        datos = []

        for evento in self.eventos:

            datos.append({
                "codigo": evento.codigo,
                "codigo_cultivo": evento.codigo_cultivo,
                "tipo": evento.tipo,
                "fecha": evento.fecha,
                "descripcion": evento.descripcion
            })

        try:

            with open(
                self.archivo,
                "w",
                encoding="utf-8"
            ) as archivo:

                json.dump(
                    datos,
                    archivo,
                    indent=4,
                    ensure_ascii=False
                )

        except OSError:

            print(
                "No se pudieron guardar "
                "los eventos del calendario."
            )

    # =====================================================
    # CARGAR DATOS
    # =====================================================

    def cargar_datos(self):

        if not os.path.exists(self.archivo):
            return

        try:

            with open(
                self.archivo,
                "r",
                encoding="utf-8"
            ) as archivo:

                datos = json.load(archivo)

            for dato in datos:

                evento = EventoCalendario(
                    codigo=dato["codigo"],
                    codigo_cultivo=dato["codigo_cultivo"],
                    tipo=dato["tipo"],
                    # Si la fecha vieja venía sin cero (2026-10-8), aquí se corrige
                    fecha=normalizar_fecha_segura(dato["fecha"]),
                    descripcion=dato.get(
                        "descripcion",
                        ""
                    )
                )

                self.eventos.append(evento)
                self.arbol.insertar(evento)

        except (
            json.JSONDecodeError,
            KeyError,
            OSError
        ):

            print(
                "No se pudieron cargar "
                "los eventos guardados."
            )

    # =====================================================
    # PREDICCIÓN DE COSECHA
    # =====================================================

    def calcular_prediccion(
        self,
        codigo_cultivo,
        nombre_cultivo,
        fecha_siembra_str
    ):

        # Normalizar el tipo de cultivo
        key_cultivo = (
            nombre_cultivo
            .lower()
            .strip()
        )

        # Buscar días de maduración
        # Si no existe el cultivo,
        # se utiliza un valor de 90 días.
        dias_ciclo = self.dias_maduracion.get(
            key_cultivo,
            90
        )

        # Validar fecha de siembra
        try:

            fecha_siembra = datetime.strptime(
                fecha_siembra_str,
                "%Y-%m-%d"
            )

        except ValueError:

            raise ValueError(
                "El formato de fecha debe ser YYYY-MM-DD"
            )

        # Calcular fecha estimada
        fecha_estimada_obj = (
            fecha_siembra +
            timedelta(days=dias_ciclo)
        )

        # Fecha actual
        hoy = datetime.now()

        # Calcular días restantes
        dias_restantes = (
            fecha_estimada_obj - hoy
        ).days

        # Determinar estado
        if dias_restantes > 15:

            estado = "En crecimiento"

        elif 0 <= dias_restantes <= 15:

            estado = "Próximo a cosechar"

        else:

            estado = "Listo para cosecha"

        # Convertir fecha a texto
        fecha_estimada = (
            fecha_estimada_obj.strftime(
                "%Y-%m-%d"
            )
        )

        return PrediccionCosecha(
            codigo_cultivo=codigo_cultivo,
            fecha_estimada=fecha_estimada,
            dias_restantes=max(
                0,
                dias_restantes
            ),
            estado=estado
        )

    # =====================================================
    # MOSTRAR CALENDARIO
    # =====================================================

    def mostrar_calendario(self):

        if not self.eventos:

            print(
                "No hay eventos registrados "
                "en el calendario."
            )

            return

        print(
            "\n--- AGENDA DE EVENTOS AGRÍCOLAS ---"
        )

        eventos_ordenados = self.eventos_ordenados()

        for evento in eventos_ordenados:

            print(evento)


# =========================================================
# PRUEBA
# =========================================================

if __name__ == "__main__":

    gestor = GestorCalendario()

    evento1 = EventoCalendario(
        codigo="EVT001",
        codigo_cultivo="CULT001",
        tipo="Fertilización",
        fecha="2026-09-01",
        descripcion="Aplicar fertilizante NPK"
    )

    gestor.agregar_evento(evento1)

    evento2 = EventoCalendario(
        codigo="EVT002",
        codigo_cultivo="CULT001",
        tipo="Riego",
        fecha="2026-09-20",
        descripcion="Riego por goteo programado"
    )

    gestor.agregar_evento(evento2)

    gestor.mostrar_calendario()

    print(
        "\n--- PREDICCIÓN DE COSECHAS ---"
    )

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