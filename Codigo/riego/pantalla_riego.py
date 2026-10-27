# pantalla_riego.py
#
# Pantalla RIEGO de AgroSmart. Junta dos cosas en un solo lugar:
#   1) El riego con sensor (simulado): revisa la humedad de cada cultivo.
#   2) El plan de agua (antes estaba en "Optimizar"):
#        - Cola            -> riegos pendientes
#        - Lista enlazada  -> historial de riegos hechos
#        - Voraz           -> repartir el agua que tengo entre mis cultivos
#        - Grafo/Dijkstra  -> distancias entre parcelas y mejor recorrido

import os
import sys

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget

# Rutas para encontrar los demás archivos del proyecto
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(_BASE, "..", "riego"))
sys.path.append(os.path.join(_BASE, "..", "modelos"))
sys.path.append(os.path.join(_BASE, "..", "algoritmos"))
sys.path.append(os.path.join(_BASE, "..", "estructuras"))

from gestor_cultivos import GestorCultivos
from unidades import texto_terreno
from riego_agrosmart import GestorRiego, ControladorRiego
from planificador import Planificador, PUNTO_INICIO
from dijkstra import dijkstra


# ============================================================
# COLORES - ROSA PALO
# ============================================================

COLOR_FONDO = (0.18, 0.12, 0.14, 1)

COLOR_ROSA_PALO = (0.72, 0.48, 0.54, 1)
COLOR_ROSA_CLARO = (0.90, 0.72, 0.76, 1)

COLOR_TEXTO = (0.96, 0.93, 0.94, 1)
COLOR_TEXTO_SECUNDARIO = (0.76, 0.68, 0.71, 1)

COLOR_TARJETA = (0.29, 0.21, 0.24, 1)
COLOR_TARJETA_CLARA = (0.38, 0.28, 0.32, 1)

COLOR_EXITO = (0.55, 0.82, 0.62, 1)
COLOR_ERROR = (0.95, 0.50, 0.55, 1)
COLOR_INFO = (0.65, 0.78, 0.88, 1)

# Compatibilidad con app_principal.py
COLOR_AZUL_PRINCIPAL = COLOR_ROSA_PALO
COLOR_VERDE_PRINCIPAL = COLOR_ROSA_PALO
COLOR_VERDE_CLARO = COLOR_ROSA_CLARO


# ============================================================
# GESTORES (uno solo para toda la pantalla)
# ============================================================

gestor_cultivos = GestorCultivos()
gestor_riego = GestorRiego(gestor_cultivos)
controlador_riego = ControladorRiego(gestor_riego)
planificador = Planificador()

TEXTO_ELEGIR = "Elige un lugar..."


# ============================================================
# AYUDANTES PARA DIBUJAR (así no repetimos código)
# ============================================================

def crear_etiqueta(texto, color=COLOR_TEXTO, tamano=14, negrita=False,
                   alto_min=30, alineacion="left"):
    # Etiqueta que crece sola según el texto que tenga
    etiqueta = Label(
        text=str(texto),
        color=color,
        font_size=dp(tamano),
        bold=negrita,
        halign=alineacion,
        valign="middle",
        size_hint_y=None,
        height=dp(alto_min)
    )
    etiqueta.bind(
        width=lambda instancia, ancho: setattr(
            instancia, "text_size", (ancho, None)
        )
    )
    etiqueta.bind(
        texture_size=lambda instancia, tam: setattr(
            instancia, "height", max(dp(alto_min), tam[1] + dp(6))
        )
    )
    return etiqueta


def crear_boton(texto, accion, color=COLOR_ROSA_PALO, alto=48):
    boton = Button(
        text=texto,
        size_hint_y=None,
        height=dp(alto),
        background_normal="",
        background_color=color,
        color=COLOR_TEXTO,
        font_size=dp(14),
        bold=True
    )
    boton.bind(on_release=lambda instancia: accion())
    return boton


def crear_titulo(texto):
    return crear_etiqueta(texto, COLOR_TEXTO, 18, True, 35)


def crear_separador():
    separador = Widget(size_hint_y=None, height=dp(2))
    with separador.canvas:
        Color(*COLOR_ROSA_PALO)
        linea = RoundedRectangle(
            pos=separador.pos, size=separador.size, radius=[dp(1)]
        )
    separador.bind(
        pos=lambda instancia, valor: setattr(linea, "pos", valor),
        size=lambda instancia, valor: setattr(linea, "size", valor)
    )
    return separador


def valor_de(datos, *claves):
    # Busca el primer dato que exista con alguno de esos nombres
    # (sirve para diccionarios y también para objetos)
    for clave in claves:
        if isinstance(datos, dict):
            if datos.get(clave) is not None:
                return datos[clave]
        elif getattr(datos, clave, None) is not None:
            return getattr(datos, clave)
    return None


class CajaTarjeta(BoxLayout):
    # Caja con fondo de tarjeta que crece según lo que tenga adentro
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[dp(18), dp(12)],
            spacing=dp(6),
            size_hint_y=None,
            **kwargs
        )
        self.bind(minimum_height=self.setter("height"))

        with self.canvas.before:
            Color(*COLOR_TARJETA)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self.actualizar_rect, size=self.actualizar_rect)

    def actualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size


# ============================================================
# TARJETA DE CULTIVO
# ============================================================

class TarjetaCultivo(BoxLayout):

    def __init__(self, cultivo, callback, seleccionado=False, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=[dp(18), dp(10)],
            spacing=dp(2),
            size_hint_y=None,
            height=dp(82),
            **kwargs
        )

        self.cultivo = cultivo
        self.callback = callback
        self.seleccionado = seleccionado

        with self.canvas.before:
            self.color_fondo = Color(
                *(COLOR_TARJETA_CLARA if seleccionado else COLOR_TARJETA)
            )
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )

        self.bind(pos=self.actualizar_rect, size=self.actualizar_rect)

        nombre = Label(
            text=str(cultivo.nombre),
            color=COLOR_TEXTO,
            font_size=dp(17),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(30)
        )
        nombre.bind(
            size=lambda instancia, valor: setattr(instancia, "text_size", valor)
        )

        detalles = Label(
            text=(
                f"{cultivo.tipo}  •  "
                f"Parcela {cultivo.numero_parcela}  •  "
                f"{texto_terreno(cultivo.tamano_parcela)}"
            ),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(12),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )
        detalles.bind(
            size=lambda instancia, valor: setattr(instancia, "text_size", valor)
        )

        self.add_widget(nombre)
        self.add_widget(detalles)

    def actualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.callback(self.cultivo)
            return True
        return super().on_touch_down(touch)


# ============================================================
# PANTALLA RIEGO
# ============================================================

class PantallaRiego(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(do_scroll_x=False, do_scroll_y=True, **kwargs)

        self.cultivo_seleccionado = None
        self.gestor_actual = gestor_cultivos

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(20), dp(20), dp(20), dp(30)],
            size_hint_y=None
        )
        self.contenedor.bind(minimum_height=self.contenedor.setter("height"))
        self.add_widget(self.contenedor)

        self.crear_interfaz()

        Clock.schedule_once(lambda dt: self.actualizar_lista(), 0)

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):
        c = self.contenedor

        c.add_widget(crear_etiqueta(
            "RIEGO", COLOR_ROSA_CLARO, 30, True, 48, "center"
        ))
        c.add_widget(crear_etiqueta(
            "Control de riego y plan de agua para tus cultivos",
            COLOR_TEXTO_SECUNDARIO, 14, False, 35, "center"
        ))

        # ---------- TUS CULTIVOS ----------
        c.add_widget(crear_titulo("TUS CULTIVOS"))
        c.add_widget(crear_etiqueta(
            "Toca un cultivo para revisarlo.", COLOR_TEXTO_SECUNDARIO, 12
        ))

        self.lista_cultivos = BoxLayout(
            orientation="vertical", spacing=dp(10), size_hint_y=None
        )
        self.lista_cultivos.bind(
            minimum_height=self.lista_cultivos.setter("height")
        )
        c.add_widget(self.lista_cultivos)

        c.add_widget(crear_boton(
            "Revisar y regar todos los cultivos", self.revisar_y_regar_todos
        ))

        c.add_widget(crear_separador())

        # ---------- ESTADO DEL RIEGO ----------
        c.add_widget(crear_titulo("ESTADO DEL RIEGO"))

        self.resultado_contenedor = CajaTarjeta()
        self.resultado_contenedor.add_widget(crear_etiqueta(
            "Selecciona un cultivo para revisar su riego.",
            COLOR_TEXTO_SECUNDARIO, 14, False, 60, "center"
        ))
        c.add_widget(self.resultado_contenedor)

        c.add_widget(crear_separador())

        # ---------- PLAN DE AGUA: PENDIENTES E HISTORIAL ----------
        c.add_widget(crear_titulo("PLAN DE AGUA"))
        c.add_widget(crear_etiqueta(
            "Selecciona un cultivo arriba y agrégalo a la lista de pendientes. "
            "Cuando lo riegues, márcalo como regado.",
            COLOR_TEXTO_SECUNDARIO, 12
        ))

        c.add_widget(crear_boton(
            "Agregar el cultivo seleccionado a pendientes",
            self.agregar_pendiente
        ))
        c.add_widget(crear_boton(
            "Marcar el siguiente pendiente como regado",
            self.marcar_regado, COLOR_TARJETA_CLARA
        ))

        self.caja_pendientes = CajaTarjeta()
        c.add_widget(self.caja_pendientes)

        self.caja_historial = CajaTarjeta()
        c.add_widget(self.caja_historial)

        c.add_widget(crear_separador())

        # ---------- REPARTIR MI AGUA ----------
        c.add_widget(crear_titulo("REPARTIR MI AGUA"))
        c.add_widget(crear_etiqueta(
            "Escribe cuántos litros tienes. AgroSmart te dice cuánto darle a "
            "cada cultivo para aprovechar mejor el agua (primero los que más "
            "lo necesitan).",
            COLOR_TEXTO_SECUNDARIO, 12
        ))

        self.campo_litros = TextInput(
            hint_text="Litros de agua que tengo (ej. 4000)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_active="",
            background_color=(0.96, 0.90, 0.92, 1),
            foreground_color=(0.18, 0.12, 0.14, 1),
            hint_text_color=(0.45, 0.38, 0.40, 1),
            padding=[dp(15), dp(12), dp(15), dp(12)]
        )
        c.add_widget(self.campo_litros)

        c.add_widget(crear_boton("Repartir mi agua", self.repartir_agua))

        self.caja_reparto = CajaTarjeta()
        self.caja_reparto.add_widget(crear_etiqueta(
            "Aquí aparecerá el reparto.", COLOR_TEXTO_SECUNDARIO, 13
        ))
        c.add_widget(self.caja_reparto)

        c.add_widget(crear_separador())

        # ---------- DISTANCIAS Y RECORRIDO ----------
        c.add_widget(crear_titulo("DISTANCIAS Y RECORRIDO"))
        c.add_widget(crear_etiqueta(
            "Tus parcelas están en lugares distintos. Anota cuántos "
            "kilómetros hay entre dos lugares (tu casa o una parcela) y "
            "AgroSmart calcula el camino más corto y el mejor orden para "
            "visitar tus pendientes.",
            COLOR_TEXTO_SECUNDARIO, 12
        ))

        self.spinner_desde = self._crear_spinner()
        self.spinner_hasta = self._crear_spinner()
        c.add_widget(crear_etiqueta("Desde:", COLOR_TEXTO, 13))
        c.add_widget(self.spinner_desde)
        c.add_widget(crear_etiqueta("Hasta:", COLOR_TEXTO, 13))
        c.add_widget(self.spinner_hasta)

        self.campo_km = TextInput(
            hint_text="Distancia en kilómetros (ej. 2.5)",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_active="",
            background_color=(0.96, 0.90, 0.92, 1),
            foreground_color=(0.18, 0.12, 0.14, 1),
            hint_text_color=(0.45, 0.38, 0.40, 1),
            padding=[dp(15), dp(12), dp(15), dp(12)]
        )
        c.add_widget(self.campo_km)

        c.add_widget(crear_boton("Guardar distancia", self.guardar_distancia))

        self.caja_distancias = CajaTarjeta()
        c.add_widget(self.caja_distancias)

        c.add_widget(crear_boton(
            "Camino más corto al cultivo seleccionado",
            self.ver_camino_corto, COLOR_TARJETA_CLARA
        ))
        c.add_widget(crear_boton(
            "Mejor orden para visitar mis pendientes",
            self.ver_recorrido, COLOR_TARJETA_CLARA
        ))
        c.add_widget(crear_boton(
            "Borrar todas las distancias",
            self.borrar_distancias, (0.55, 0.30, 0.34, 1)
        ))

        self.caja_recorrido = CajaTarjeta()
        self.caja_recorrido.add_widget(crear_etiqueta(
            "Aquí aparecerá el recorrido.", COLOR_TEXTO_SECUNDARIO, 13
        ))
        c.add_widget(self.caja_recorrido)

    def _crear_spinner(self):
        return Spinner(
            text=TEXTO_ELEGIR,
            values=[],
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=COLOR_TARJETA_CLARA,
            color=COLOR_TEXTO
        )

    # ========================================================
    # NOMBRES DE LUGARES (para mostrar nombres en vez de códigos)
    # ========================================================

    def _nombres(self):
        nombres = {PUNTO_INICIO: "Mi casa"}
        for cultivo in self.gestor_actual.lista_cultivos:
            nombres[cultivo.codigo] = cultivo.nombre
        return nombres

    def _codigo_de_spinner(self, texto):
        # El spinner muestra "CULT001 - Maiz parcela 1"; aquí sacamos "CULT001"
        if texto == TEXTO_ELEGIR:
            return None
        return texto.split(" - ")[0].strip()

    def _opciones_lugares(self):
        opciones = [f"{PUNTO_INICIO} - Mi casa"]
        for cultivo in self.gestor_actual.lista_cultivos:
            opciones.append(f"{cultivo.codigo} - {cultivo.nombre}")
        return opciones

    # ========================================================
    # ACTUALIZAR LISTA DE CULTIVOS
    # ========================================================

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        # Volvemos a cargar los cultivos guardados
        self.gestor_actual = GestorCultivos()
        gestor_riego.gestor_cultivos = self.gestor_actual
        gestor_riego.sincronizar_con_cultivos()

        cultivos = self.gestor_actual.lista_cultivos

        if not cultivos:
            self.lista_cultivos.add_widget(crear_etiqueta(
                "Todavía no tienes cultivos registrados.",
                COLOR_TEXTO_SECUNDARIO, 14, False, 60, "center"
            ))
        else:
            for cultivo in cultivos:
                self.lista_cultivos.add_widget(TarjetaCultivo(
                    cultivo=cultivo,
                    callback=self.revisar_cultivo,
                    seleccionado=(
                        self.cultivo_seleccionado is not None
                        and self.cultivo_seleccionado.codigo == cultivo.codigo
                    )
                ))

        # Opciones de los dos spinners de distancias
        opciones = self._opciones_lugares()
        self.spinner_desde.values = opciones
        self.spinner_hasta.values = opciones
        if self.spinner_desde.text not in opciones:
            self.spinner_desde.text = TEXTO_ELEGIR
        if self.spinner_hasta.text not in opciones:
            self.spinner_hasta.text = TEXTO_ELEGIR

        self.actualizar_plan()

    # ========================================================
    # SELECCIONAR / REVISAR UN CULTIVO
    # ========================================================

    def revisar_cultivo(self, cultivo):

        self.cultivo_seleccionado = cultivo

        try:
            resultado = controlador_riego.revisar_zona(cultivo.codigo)
            self.mostrar_resultado(resultado, cultivo)
            self.actualizar_seleccion_visual()
        except Exception as e:
            self.mostrar_error(f"No se pudo revisar el riego:\n{e}")

    def actualizar_seleccion_visual(self):
        for widget in self.lista_cultivos.children:
            if isinstance(widget, TarjetaCultivo):
                seleccionado = (
                    self.cultivo_seleccionado is not None
                    and widget.cultivo.codigo == self.cultivo_seleccionado.codigo
                )
                widget.color_fondo.rgba = (
                    COLOR_TARJETA_CLARA if seleccionado else COLOR_TARJETA
                )

    # ========================================================
    # REVISAR TODOS
    # ========================================================

    def revisar_y_regar_todos(self):

        try:
            resultados = controlador_riego.revisar_y_regar_todas()

            if not resultados:
                self.mostrar_mensaje("No hay cultivos registrados para revisar.")
                return

            self.mostrar_resultados_todos(resultados)
            self.actualizar_lista()

        except Exception as e:
            self.mostrar_error(f"No se pudo realizar la revisión:\n{e}")

    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    def mostrar_resultado(self, resultado, cultivo):

        caja = self.resultado_contenedor
        caja.clear_widgets()

        nombre = valor_de(resultado, "nombre", "cultivo") or cultivo.nombre
        humedad = valor_de(resultado, "humedad", "humedad_actual")
        estado = str(valor_de(resultado, "estado") or "desconocido")
        mensaje = valor_de(resultado, "mensaje") or "Sin información adicional."

        caja.add_widget(crear_etiqueta(nombre, COLOR_ROSA_CLARO, 21, True, 35))

        if humedad is not None:
            caja.add_widget(crear_etiqueta(
                f"Humedad actual: {float(humedad):.1f}%", COLOR_TEXTO, 14
            ))

        caja.add_widget(crear_etiqueta(
            f"Estado: {estado.upper()}", self.color_estado(estado), 14, True
        ))
        caja.add_widget(crear_etiqueta(mensaje, COLOR_TEXTO, 14))

        minutos = valor_de(resultado, "minutos", "duracion_minutos")
        if minutos is not None:
            self.agregar_dato(f"Duración estimada: {minutos} min")

        litros = valor_de(resultado, "litros", "litros_estimados")
        if litros is not None:
            self.agregar_dato(f"Agua usada por el sensor: {float(litros):.1f} litros")

        probabilidad = valor_de(resultado, "probabilidad", "probabilidad_lluvia")
        if probabilidad is not None:
            self.agregar_dato(f"Probabilidad de lluvia: {float(probabilidad):.0f}%")

        lluvia = valor_de(resultado, "milimetros_lluvia", "milimetros")
        if lluvia is not None:
            self.agregar_dato(f"Lluvia estimada: {float(lluvia):.1f} mm")

        # Recomendación del plan de agua para este cultivo
        try:
            rec = planificador.recomendar(cultivo)
            texto_estado, _ = planificador.estado_riego(cultivo, rec)
            self.agregar_dato(
                f"Plan recomendado: {rec['litros']:,.0f} litros cada "
                f"{rec['dias']} días ({rec['etapa_texto']})"
            )
            self.agregar_dato(texto_estado)
        except Exception:
            pass

    def agregar_dato(self, texto):
        self.resultado_contenedor.add_widget(crear_etiqueta(
            texto, COLOR_TEXTO_SECUNDARIO, 13, False, 25
        ))

    def mostrar_resultados_todos(self, resultados):

        caja = self.resultado_contenedor
        caja.clear_widgets()

        caja.add_widget(crear_etiqueta(
            "Revisión de todos los cultivos", COLOR_ROSA_CLARO, 20, True, 35
        ))

        for resultado in resultados:
            nombre = valor_de(resultado, "nombre", "cultivo") or "Cultivo"
            estado = str(valor_de(resultado, "estado") or "desconocido")
            mensaje = valor_de(resultado, "mensaje") or ""

            caja.add_widget(crear_etiqueta(
                f"{nombre}: {estado.upper()}\n{mensaje}",
                self.color_estado(estado), 12, False, 40
            ))

    def color_estado(self, estado):
        estado = str(estado).lower()
        if estado in ("regado", "correcto"):
            return COLOR_EXITO
        if estado == "lluvia":
            return COLOR_INFO
        if estado == "error":
            return COLOR_ERROR
        return COLOR_TEXTO

    def mostrar_mensaje(self, texto):
        self.resultado_contenedor.clear_widgets()
        self.resultado_contenedor.add_widget(crear_etiqueta(
            texto, COLOR_TEXTO_SECUNDARIO, 14, False, 60, "center"
        ))

    def mostrar_error(self, texto):
        self.resultado_contenedor.clear_widgets()
        self.resultado_contenedor.add_widget(crear_etiqueta(
            texto, COLOR_ERROR, 14, False, 60, "center"
        ))

    # ========================================================
    # PLAN DE AGUA: COLA (pendientes) Y LISTA ENLAZADA (historial)
    # ========================================================

    def actualizar_plan(self):
        nombres = self._nombres()

        # --- Pendientes (cola) ---
        self.caja_pendientes.clear_widgets()
        self.caja_pendientes.add_widget(crear_etiqueta(
            "Pendientes por regar (el primero es el siguiente)",
            COLOR_ROSA_CLARO, 15, True
        ))
        pendientes = planificador.cola.a_lista()
        if not pendientes:
            self.caja_pendientes.add_widget(crear_etiqueta(
                "No hay riegos pendientes.", COLOR_TEXTO_SECUNDARIO, 13
            ))
        else:
            for numero, codigo in enumerate(pendientes, 1):
                self.caja_pendientes.add_widget(crear_etiqueta(
                    f"{numero}. {nombres.get(codigo, codigo)}",
                    COLOR_TEXTO, 13, False, 25
                ))

        # --- Historial (lista enlazada) ---
        self.caja_historial.clear_widgets()
        self.caja_historial.add_widget(crear_etiqueta(
            "Riegos ya hechos (los más nuevos primero)",
            COLOR_ROSA_CLARO, 15, True
        ))
        historial = planificador.historial.a_lista()
        if not historial:
            self.caja_historial.add_widget(crear_etiqueta(
                "Todavía no hay riegos anotados.", COLOR_TEXTO_SECUNDARIO, 13
            ))
        else:
            for registro in historial[:8]:
                codigo = registro.get("codigo", "?")
                self.caja_historial.add_widget(crear_etiqueta(
                    f"{nombres.get(codigo, codigo)}  -  {registro.get('momento', '')}",
                    COLOR_TEXTO, 13, False, 25
                ))

        # --- Distancias guardadas ---
        self.caja_distancias.clear_widgets()
        self.caja_distancias.add_widget(crear_etiqueta(
            "Distancias guardadas", COLOR_ROSA_CLARO, 15, True
        ))
        if not planificador.canales:
            self.caja_distancias.add_widget(crear_etiqueta(
                "Todavía no has guardado distancias.", COLOR_TEXTO_SECUNDARIO, 13
            ))
        else:
            for canal in planificador.canales:
                desde = nombres.get(canal["desde"], canal["desde"])
                hasta = nombres.get(canal["hasta"], canal["hasta"])
                self.caja_distancias.add_widget(crear_etiqueta(
                    f"{desde}  a  {hasta}:  {canal['km']:g} km",
                    COLOR_TEXTO, 13, False, 25
                ))

    def agregar_pendiente(self):
        if self.cultivo_seleccionado is None:
            self.mostrar_mensaje("Primero toca un cultivo de la lista.")
            return

        if planificador.programar_riego(self.cultivo_seleccionado.codigo):
            self.actualizar_plan()
        else:
            self.mostrar_mensaje(
                f"{self.cultivo_seleccionado.nombre} ya estaba en pendientes."
            )

    def marcar_regado(self):
        registro = planificador.atender_siguiente()
        if registro is None:
            self.mostrar_mensaje("No hay riegos pendientes para marcar.")
            return
        self.actualizar_plan()

    # ========================================================
    # REPARTIR MI AGUA (algoritmo voraz)
    # ========================================================

    def repartir_agua(self):
        caja = self.caja_reparto
        caja.clear_widgets()

        texto = self.campo_litros.text.strip()
        try:
            litros = float(texto)
        except ValueError:
            caja.add_widget(crear_etiqueta(
                "Escribe un número de litros, por ejemplo 4000.", COLOR_ERROR, 13
            ))
            return

        if litros <= 0:
            caja.add_widget(crear_etiqueta(
                "Los litros deben ser mayores que cero.", COLOR_ERROR, 13
            ))
            return

        cultivos = self.gestor_actual.lista_cultivos
        if not cultivos:
            caja.add_widget(crear_etiqueta(
                "Primero registra cultivos en la pantalla Cultivos.",
                COLOR_ERROR, 13
            ))
            return

        try:
            asignaciones, sobrante = planificador.repartir_agua(cultivos, litros)
        except Exception as e:
            caja.add_widget(crear_etiqueta(
                f"No se pudo repartir el agua:\n{e}", COLOR_ERROR, 13
            ))
            return

        caja.add_widget(crear_etiqueta(
            f"Reparto de {litros:,.0f} litros", COLOR_ROSA_CLARO, 16, True
        ))

        for item in asignaciones:
            nombre = valor_de(item, "nombre") or "Cultivo"
            dado = valor_de(item, "asignado", "litros_asignados", "litros_dados", "dado")
            necesita = valor_de(item, "necesidad", "necesario", "litros_necesarios")

            if dado is not None and necesita:
                porcentaje = float(dado) / float(necesita) * 100
                linea = (
                    f"{nombre}: {float(dado):,.0f} de {float(necesita):,.0f} "
                    f"litros ({porcentaje:.0f}%)"
                )
            else:
                linea = f"{nombre}: {item}"

            caja.add_widget(crear_etiqueta(linea, COLOR_TEXTO, 13, False, 25))

        caja.add_widget(crear_etiqueta(
            f"Agua que sobra: {float(sobrante):,.0f} litros",
            COLOR_EXITO, 13, True
        ))

    # ========================================================
    # DISTANCIAS Y RECORRIDO (grafo + Dijkstra)
    # ========================================================

    def guardar_distancia(self):
        desde = self._codigo_de_spinner(self.spinner_desde.text)
        hasta = self._codigo_de_spinner(self.spinner_hasta.text)

        if desde is None or hasta is None:
            self.mostrar_recorrido_error("Elige el lugar de inicio y el de llegada.")
            return

        if desde == hasta:
            self.mostrar_recorrido_error("Elige dos lugares distintos.")
            return

        try:
            km = float(self.campo_km.text.strip())
        except ValueError:
            self.mostrar_recorrido_error("Escribe la distancia en kilómetros (ej. 2.5).")
            return

        if km <= 0:
            self.mostrar_recorrido_error("La distancia debe ser mayor que cero.")
            return

        planificador.agregar_canal(desde, hasta, km)
        self.campo_km.text = ""
        self.actualizar_plan()
        self.mostrar_recorrido_lineas(["Distancia guardada."], COLOR_EXITO)

    def borrar_distancias(self):
        planificador.borrar_canales()
        self.actualizar_plan()
        self.mostrar_recorrido_lineas(["Se borraron todas las distancias."], COLOR_TEXTO)

    def ver_camino_corto(self):
        if self.cultivo_seleccionado is None:
            self.mostrar_recorrido_error("Primero toca un cultivo de la lista.")
            return

        codigo = self.cultivo_seleccionado.codigo
        grafo = planificador.grafo

        if not grafo.existe(codigo):
            self.mostrar_recorrido_error(
                "Ese cultivo todavía no tiene distancias guardadas."
            )
            return

        distancias, previos = dijkstra(grafo, PUNTO_INICIO)
        km = distancias[codigo]

        if km == float("inf"):
            self.mostrar_recorrido_error(
                "No hay camino registrado desde tu casa hasta ese cultivo. "
                "Guarda más distancias."
            )
            return

        # Armamos el camino yendo hacia atrás: del destino hasta la casa
        nombres = self._nombres()
        ruta = []
        actual = codigo
        while actual is not None and len(ruta) < 200:
            ruta.append(nombres.get(actual, actual))
            actual = previos.get(actual) if isinstance(previos, dict) else None
        ruta.reverse()

        self.mostrar_recorrido_lineas([
            f"Camino más corto a {self.cultivo_seleccionado.nombre}:",
            "  >  ".join(ruta),
            f"Distancia total: {km:g} km"
        ])

    def ver_recorrido(self):
        pendientes = planificador.cola.a_lista()

        if not pendientes:
            self.mostrar_recorrido_error(
                "No hay riegos pendientes. Agrega cultivos a pendientes primero."
            )
            return

        orden, total, sin_camino = planificador.orden_de_visita(pendientes)
        nombres = self._nombres()

        lineas = []
        if orden:
            lugares = ["Mi casa"] + [nombres.get(c, c) for c in orden]
            lineas.append("Visita en este orden:")
            lineas.append("  >  ".join(lugares))
            lineas.append(f"Recorrido total: {total:g} km")

        if sin_camino:
            faltan = ", ".join(nombres.get(c, c) for c in sin_camino)
            lineas.append(f"Faltan distancias para llegar a: {faltan}")

        if not lineas:
            lineas.append("No se pudo calcular el recorrido.")

        self.mostrar_recorrido_lineas(lineas)

    def mostrar_recorrido_lineas(self, lineas, color=COLOR_TEXTO):
        self.caja_recorrido.clear_widgets()
        for linea in lineas:
            self.caja_recorrido.add_widget(crear_etiqueta(linea, color, 13))

    def mostrar_recorrido_error(self, texto):
        self.mostrar_recorrido_lineas([texto], COLOR_ERROR)