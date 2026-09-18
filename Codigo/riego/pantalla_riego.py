# pantalla_riego.py

import os
import sys

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget

# Rutas
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "riego"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modelos"))

from gestor_cultivos import GestorCultivos
from riego_agrosmart import GestorRiego, ControladorRiego, normalizar_codigo




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
# GESTORES
# ============================================================

gestor_cultivos = GestorCultivos()
gestor_riego = GestorRiego(gestor_cultivos)
controlador_riego = ControladorRiego(gestor_riego)


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
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
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
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        detalles = Label(
            text=(
                f"{cultivo.tipo}  •  "
                f"Parcela {cultivo.numero_parcela}  •  "
                f"{cultivo.tamano_parcela} ha"
            ),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(12),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )

        detalles.bind(
            size=lambda instance, value: setattr(
                instance, "text_size", value
            )
        )

        self.add_widget(nombre)
        self.add_widget(detalles)

    def actualizar_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def seleccionar(self):
        self.callback(self.cultivo)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.seleccionar()
            return True

        return super().on_touch_down(touch)


# ============================================================
# PANTALLA RIEGO
# ============================================================

class PantallaRiego(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(
            do_scroll_x=False,
            do_scroll_y=True,
            **kwargs
        )

        self.cultivo_seleccionado = None

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(14),
            padding=[dp(20), dp(20), dp(20), dp(30)],
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        self.add_widget(self.contenedor)

        self.crear_interfaz()

        Clock.schedule_once(
            lambda dt: self.actualizar_lista(),
            0
        )

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # TÍTULO
        titulo = Label(
            text="RIEGO",
            color=COLOR_ROSA_CLARO,
            font_size=dp(30),
            bold=True,
            size_hint_y=None,
            height=dp(48)
        )

        self.contenedor.add_widget(titulo)

        subtitulo = Label(
            text="Control inteligente de riego para tus cultivos",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(14),
            size_hint_y=None,
            height=dp(35)
        )

        self.contenedor.add_widget(subtitulo)

        # SECCIÓN CULTIVOS
        titulo_cultivos = Label(
            text="TUS CULTIVOS",
            color=COLOR_TEXTO,
            font_size=dp(18),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )

        titulo_cultivos.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(titulo_cultivos)

        # LISTA DE CULTIVOS
        self.lista_cultivos = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.contenedor.add_widget(self.lista_cultivos)

        # BOTÓN GENERAL
        self.boton_todos = Button(
            text="Revisar y regar todos los cultivos",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=COLOR_ROSA_PALO,
            color=COLOR_TEXTO,
            font_size=dp(14),
            bold=True
        )

        self.boton_todos.bind(
            on_release=lambda instance: self.revisar_y_regar_todos()
        )

        self.contenedor.add_widget(self.boton_todos)

        # SEPARADOR
        separador = Widget(
            size_hint_y=None,
            height=dp(2)
        )

        with separador.canvas:
            Color(*COLOR_ROSA_PALO)
            self.linea = RoundedRectangle(
                pos=separador.pos,
                size=separador.size,
                radius=[dp(1)]
            )

        separador.bind(
            pos=lambda instance, value: setattr(
                self.linea,
                "pos",
                value
            ),
            size=lambda instance, value: setattr(
                self.linea,
                "size",
                value
            )
        )

        self.contenedor.add_widget(separador)

        # ESTADO
        titulo_estado = Label(
            text="ESTADO DEL RIEGO",
            color=COLOR_TEXTO,
            font_size=dp(18),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )

        titulo_estado.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(titulo_estado)

        # RESULTADO
        self.resultado_contenedor = BoxLayout(
            orientation="vertical",
            padding=[dp(18), dp(15)],
            spacing=dp(6),
            size_hint_y=None,
            height=dp(250)
        )

        with self.resultado_contenedor.canvas.before:
            self.color_resultado = Color(*COLOR_TARJETA)
            self.rect_resultado = RoundedRectangle(
                pos=self.resultado_contenedor.pos,
                size=self.resultado_contenedor.size,
                radius=[dp(12)]
            )

        self.resultado_contenedor.bind(
            pos=self.actualizar_rect_resultado,
            size=self.actualizar_rect_resultado
        )

        mensaje_inicial = Label(
            text="Selecciona un cultivo para revisar su riego.",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(14),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(80)
        )

        mensaje_inicial.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            mensaje_inicial
        )

        self.contenedor.add_widget(
            self.resultado_contenedor
        )

        Clock.schedule_once(
            self.actualizar_alturas,
            0
        )

    # ========================================================
    # ACTUALIZAR ALTURAS
    # ========================================================

    def actualizar_alturas(self, *args):

        cantidad = len(self.lista_cultivos.children)

        if cantidad == 0:
            self.lista_cultivos.height = dp(60)
        else:
            self.lista_cultivos.height = (
                cantidad * dp(82)
                + max(0, cantidad - 1) * dp(10)
            )

        self.contenedor.do_layout()

    # ========================================================
    # RECTÁNGULO RESULTADO
    # ========================================================

    def actualizar_rect_resultado(self, *args):
        self.rect_resultado.pos = (
            self.resultado_contenedor.pos
        )
        self.rect_resultado.size = (
            self.resultado_contenedor.size
        )

    # ========================================================
    # ACTUALIZAR LISTA
    # ========================================================

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        # Volvemos a cargar los cultivos guardados
        gestor_actual = GestorCultivos()

        gestor_riego.gestor_cultivos = gestor_actual

        gestor_riego.sincronizar_con_cultivos()

        cultivos = gestor_actual.lista_cultivos

        # Si no hay cultivos
        if not cultivos:

            mensaje = Label(
                text="Todavía no tienes cultivos registrados.",
                color=COLOR_TEXTO_SECUNDARIO,
                font_size=dp(14),
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(60)
            )

            mensaje.bind(
                size=lambda instance, value: setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.lista_cultivos.add_widget(mensaje)

        else:

            # Crear tarjeta para cada cultivo
            for cultivo in cultivos:

                tarjeta = TarjetaCultivo(
                    cultivo=cultivo,
                    callback=self.revisar_cultivo,
                    seleccionado=(
                        self.cultivo_seleccionado is not None
                        and self.cultivo_seleccionado.codigo
                        == cultivo.codigo
                    )
                )

                self.lista_cultivos.add_widget(tarjeta)

        Clock.schedule_once(
            self.actualizar_alturas,
            0
        )

    # ========================================================
    # SELECCIONAR CULTIVO
    # ========================================================

    def revisar_cultivo(self, cultivo):

        self.cultivo_seleccionado = cultivo

        try:
            resultado = controlador_riego.revisar_zona(
                cultivo.codigo
            )

            self.mostrar_resultado(
                resultado,
                cultivo
            )

            self.actualizar_lista_seleccionada()

        except Exception as e:

            self.mostrar_error(
                f"No se pudo revisar el riego:\n{e}"
            )

    # ========================================================
    # ACTUALIZAR SELECCIÓN VISUAL
    # ========================================================

    def actualizar_lista_seleccionada(self):

        for widget in self.lista_cultivos.children:

            if isinstance(widget, TarjetaCultivo):

                seleccionado = (
                    self.cultivo_seleccionado is not None
                    and widget.cultivo.codigo
                    == self.cultivo_seleccionado.codigo
                )

                widget.color_fondo.rgba = (
                    COLOR_TARJETA_CLARA
                    if seleccionado
                    else COLOR_TARJETA
                )

    # ========================================================
    # REVISAR TODOS
    # ========================================================

    def revisar_y_regar_todos(self):

        try:

            resultados = controlador_riego.revisar_y_regar_todas()

            if not resultados:

                self.mostrar_mensaje(
                    "No hay cultivos registrados para revisar."
                )

                return

            # Mostrar resumen de todos
            self.mostrar_resultados_todos(resultados)

            self.actualizar_lista()

        except Exception as e:

            self.mostrar_error(
                f"No se pudo realizar la revisión:\n{e}"
            )

    # ========================================================
    # MOSTRAR RESULTADO INDIVIDUAL
    # ========================================================

    def mostrar_resultado(self, resultado, cultivo):

        self.resultado_contenedor.clear_widgets()

        nombre = resultado.get(
            "cultivo",
            cultivo.nombre
        )

        humedad = resultado.get(
            "humedad",
            resultado.get("humedad_actual", None)
        )

        estado = resultado.get(
            "estado",
            "desconocido"
        )

        mensaje = resultado.get(
            "mensaje",
            "Sin información adicional."
        )

        titulo = Label(
            text=str(nombre),
            color=COLOR_ROSA_CLARO,
            font_size=dp(21),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(35)
        )

        titulo.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(titulo)

        if humedad is not None:

            humedad_label = Label(
                text=f"Humedad actual: {humedad:.1f}%",
                color=COLOR_TEXTO,
                font_size=dp(14),
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(30)
            )

            humedad_label.bind(
                size=lambda instance, value: setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.resultado_contenedor.add_widget(
                humedad_label
            )

        estado_label = Label(
            text=f"Estado: {estado.upper()}",
            color=self.color_estado(estado),
            font_size=dp(14),
            bold=True,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(30)
        )

        estado_label.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            estado_label
        )

        mensaje_label = Label(
            text=str(mensaje),
            color=COLOR_TEXTO,
            font_size=dp(14),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(50)
        )

        mensaje_label.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            mensaje_label
        )

        # Duración
        duracion = resultado.get(
            "duracion_minutos"
        )

        if duracion is not None:

            self.agregar_dato(
                f"Duración estimada: {duracion} min"
            )

        # Litros
        litros = resultado.get(
            "litros_estimados"
        )

        if litros is not None:

            self.agregar_dato(
                f"Agua estimada: {litros:.1f} litros"
            )

        # Lluvia
        probabilidad = resultado.get(
            "probabilidad_lluvia"
        )

        if probabilidad is not None:

            self.agregar_dato(
                f"Probabilidad de lluvia: {probabilidad * 100:.0f}%"
            )

        lluvia = resultado.get(
            "milimetros_lluvia"
        )

        if lluvia is not None:

            self.agregar_dato(
                f"Lluvia estimada: {lluvia:.1f} mm"
            )

    # ========================================================
    # DATOS ADICIONALES
    # ========================================================

    def agregar_dato(self, texto):

        etiqueta = Label(
            text=str(texto),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(13),
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )

        etiqueta.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            etiqueta
        )

    # ========================================================
    # MOSTRAR TODOS LOS RESULTADOS
    # ========================================================

    def mostrar_resultados_todos(self, resultados):

        self.resultado_contenedor.clear_widgets()

        titulo = Label(
            text="Revisión de todos los cultivos",
            color=COLOR_ROSA_CLARO,
            font_size=dp(20),
            bold=True,
            size_hint_y=None,
            height=dp(35)
        )

        self.resultado_contenedor.add_widget(
            titulo
        )

        for resultado in resultados:

            cultivo = resultado.get(
                "cultivo",
                "Cultivo"
            )

            estado = resultado.get(
                "estado",
                "desconocido"
            )

            mensaje = resultado.get(
                "mensaje",
                ""
            )

            texto = (
                f"{cultivo}: "
                f"{estado.upper()}\n"
                f"{mensaje}"
            )

            etiqueta = Label(
                text=texto,
                color=COLOR_TEXTO,
                font_size=dp(12),
                halign="left",
                valign="middle",
                size_hint_y=None,
                height=dp(55)
            )

            etiqueta.bind(
                size=lambda instance, value: setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.resultado_contenedor.add_widget(
                etiqueta
            )

        altura = 60 + len(resultados) * 55

        self.resultado_contenedor.height = max(
            dp(250),
            dp(altura)
        )

        Clock.schedule_once(
            self.actualizar_alturas,
            0
        )

    # ========================================================
    # COLOR SEGÚN ESTADO
    # ========================================================

    def color_estado(self, estado):

        estado = str(estado).lower()

        if estado == "regado":
            return COLOR_EXITO

        if estado == "correcto":
            return COLOR_EXITO

        if estado == "lluvia":
            return COLOR_INFO

        if estado == "error":
            return COLOR_ERROR

        return COLOR_TEXTO

    # ========================================================
    # MENSAJE
    # ========================================================

    def mostrar_mensaje(self, texto):

        self.resultado_contenedor.clear_widgets()

        mensaje = Label(
            text=str(texto),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size=dp(14),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(80)
        )

        mensaje.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            mensaje
        )

        self.resultado_contenedor.height = dp(250)

    # ========================================================
    # ERROR
    # ========================================================

    def mostrar_error(self, texto):

        self.resultado_contenedor.clear_widgets()

        mensaje = Label(
            text=str(texto),
            color=COLOR_ERROR,
            font_size=dp(14),
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(100)
        )

        mensaje.bind(
            size=lambda instance, value: setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado_contenedor.add_widget(
            mensaje
        )

        self.resultado_contenedor.height = dp(250)