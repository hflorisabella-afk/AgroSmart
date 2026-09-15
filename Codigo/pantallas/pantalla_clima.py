# pantalla_clima.py
# Pantalla visual de AgroSmart para el módulo de Clima.
# Los cultivos se obtienen desde GestorCultivos.
# La localidad se toma automáticamente del cultivo seleccionado.

import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "modelos")
)

from gestor_cultivos import GestorCultivos
from clima import (
    obtener_clima_actual,
    obtener_pronostico_dias
)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView



# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = (0.05, 0.08, 0.14, 1)

COLOR_AZUL_BOTON = (0.18, 0.42, 0.65, 1)
COLOR_AZUL_CLARO = (0.55, 0.78, 0.95, 1)

COLOR_TEXTO_CLARO = (0.92, 0.95, 0.98, 1)
COLOR_INFO = (0.55, 0.78, 0.95, 1)
COLOR_ERROR = (1, 0.55, 0.5, 1)
COLOR_EXITO = (0.55, 0.9, 0.65, 1)

COLOR_TARJETA = (0.10, 0.18, 0.28, 1)

# Compatibilidad con partes anteriores del código
COLOR_VERDE_CLARO = COLOR_AZUL_CLARO
COLOR_VERDE_PRINCIPAL = COLOR_AZUL_BOTON


Window.clearcolor = COLOR_FONDO
Window.size = (780, 850)


# ============================================================
# GESTOR PRINCIPAL DE CULTIVOS
# ============================================================

gestor_cultivos = GestorCultivos()


# ============================================================
# BOTÓN
# ============================================================

def boton_estilizado(
    texto,
    alto=45,
    color_fondo=None
):

    boton = Button(
        text=texto,
        size_hint_y=None,
        height=alto,
        background_normal="",
        background_color=(
            color_fondo
            if color_fondo
            else COLOR_VERDE_PRINCIPAL
        ),
        color=(1, 1, 1, 1),
        bold=True
    )

    return boton


# ============================================================
# PANTALLA CLIMA
# ============================================================

class PantallaClima(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.cultivo_seleccionado = None

        contenido = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            padding=15,
            spacing=10
        )

        contenido.bind(
            minimum_height=contenido.setter("height")
        )

        self.add_widget(contenido)

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = Label(
            text="AgroSmart - Clima",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=45,
            color=COLOR_VERDE_CLARO
        )

        contenido.add_widget(titulo)

        # ----------------------------------------------------
        # INFORMACIÓN
        # ----------------------------------------------------

        informacion = Label(
            text=(
                "Selecciona un cultivo para consultar "
                "el clima de su localidad."
            ),
            size_hint_y=None,
            height=45,
            font_size=15,
            color=COLOR_TEXTO_CLARO
        )

        contenido.add_widget(informacion)

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        self.mensaje = Label(
            text="",
            size_hint_y=None,
            height=40,
            font_size=15,
            color=COLOR_INFO
        )

        contenido.add_widget(self.mensaje)

        # ----------------------------------------------------
        # CULTIVO SELECCIONADO
        # ----------------------------------------------------

        self.cultivo_info = Label(
            text="Ningún cultivo seleccionado.",
            size_hint_y=None,
            height=60,
            font_size=16,
            color=COLOR_VERDE_CLARO,
            bold=True
        )

        contenido.add_widget(
            self.cultivo_info
        )

        # ----------------------------------------------------
        # LISTA DE CULTIVOS
        # ----------------------------------------------------

        contenido.add_widget(
            Label(
                text="Cultivos registrados:",
                size_hint_y=None,
                height=35,
                font_size=17,
                color=COLOR_VERDE_CLARO,
                bold=True
            )
        )

        self.lista_cultivos = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            spacing=8,
            padding=[0, 5]
        )

        self.lista_cultivos.bind(
            minimum_height=self.lista_cultivos.setter(
                "height"
            )
        )

        contenido.add_widget(
            self.lista_cultivos
        )

        # ----------------------------------------------------
        # BOTONES DE CLIMA
        # ----------------------------------------------------

        fila_botones = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=45,
            spacing=10
        )

        boton_actual = boton_estilizado(
            "Ver clima actual"
        )

        boton_actual.bind(
            on_press=self.ver_clima_actual
        )

        fila_botones.add_widget(
            boton_actual
        )

        boton_pronostico = boton_estilizado(
            "Ver pronóstico (5 días)"
        )

        boton_pronostico.bind(
            on_press=self.ver_pronostico
        )

        fila_botones.add_widget(
            boton_pronostico
        )

        contenido.add_widget(
            fila_botones
        )

        # ----------------------------------------------------
        # RESULTADO ACTUAL
        # ----------------------------------------------------

        contenido.add_widget(
            Label(
                text="Clima actual:",
                size_hint_y=None,
                height=35,
                font_size=17,
                color=COLOR_VERDE_CLARO,
                bold=True
            )
        )

        self.resultado_actual = Label(
            text="Selecciona un cultivo.",
            size_hint_y=None,
            height=130,
            font_size=15,
            color=COLOR_TEXTO_CLARO,
            halign="left",
            valign="top"
        )

        self.resultado_actual.bind(
            size=lambda inst, val:
            setattr(inst, "text_size", val)
        )

        contenido.add_widget(
            self.resultado_actual
        )

        # ----------------------------------------------------
        # PRONÓSTICO
        # ----------------------------------------------------

        contenido.add_widget(
            Label(
                text="Pronóstico:",
                size_hint_y=None,
                height=35,
                font_size=17,
                color=COLOR_VERDE_CLARO,
                bold=True
            )
        )

        self.resultado_pronostico = Label(
            text="Todavía no hay pronóstico.",
            size_hint_y=None,
            height=250,
            font_size=15,
            color=COLOR_TEXTO_CLARO,
            halign="left",
            valign="top"
        )

        self.resultado_pronostico.bind(
            size=lambda inst, val:
            setattr(inst, "text_size", val)
        )

        contenido.add_widget(
            self.resultado_pronostico
        )

        self.actualizar_lista()

    # ========================================================
    # ACTUALIZAR LISTA
    # ========================================================

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        global gestor_cultivos

        # Volvemos a leer el archivo principal.
        gestor_cultivos = GestorCultivos()

        if len(
            gestor_cultivos.lista_cultivos
        ) == 0:

            self.lista_cultivos.add_widget(
                Label(
                    text=(
                        "No hay cultivos registrados. "
                        "Primero registra uno en "
                        "Registro de Cultivos."
                    ),
                    size_hint_y=None,
                    height=50,
                    color=COLOR_TEXTO_CLARO
                )
            )

            return

        # ----------------------------------------------------
        # CREAR BOTÓN PARA CADA CULTIVO
        # ----------------------------------------------------

        for cultivo in gestor_cultivos.lista_cultivos:

            boton = Button(
                text=(
                    f"{cultivo.codigo} - "
                    f"{cultivo.nombre}\n"
                    f"Localidad: "
                    f"{cultivo.localidad} | "
                    f"Tipo: {cultivo.tipo}"
                ),
                size_hint_y=None,
                height=65,
                halign="left",
                valign="middle",
                background_normal="",
                background_color=COLOR_TARJETA,
                color=COLOR_TEXTO_CLARO
            )

            boton.bind(
                size=lambda inst, val:
                setattr(inst, "text_size", val)
            )

            boton.bind(
                on_press=lambda inst,
                cultivo=cultivo:
                self.seleccionar_cultivo(cultivo)
            )

            self.lista_cultivos.add_widget(
                boton
            )

    # ========================================================
    # SELECCIONAR CULTIVO
    # ========================================================

    def seleccionar_cultivo(self, cultivo):

        self.cultivo_seleccionado = cultivo

        self.cultivo_info.text = (
            f"Seleccionado: {cultivo.nombre}\n"
            f"Localidad: {cultivo.localidad}"
        )

        self.mensaje.color = COLOR_INFO

        self.mensaje.text = (
            "Cultivo seleccionado. "
            "Ahora puedes consultar su clima."
        )

        self.resultado_actual.text = (
            "Presiona 'Ver clima actual'."
        )

        self.resultado_pronostico.text = (
            "Presiona 'Ver pronóstico (5 días)'."
        )

    # ========================================================
    # OBTENER LOCALIDAD
    # ========================================================

    def obtener_localidad(self):

        if self.cultivo_seleccionado is None:

            self.mensaje.color = COLOR_ERROR

            self.mensaje.text = (
                "Primero selecciona un cultivo."
            )

            return None

        return (
            self.cultivo_seleccionado.localidad
        )

    # ========================================================
    # CLIMA ACTUAL
    # ========================================================

    def ver_clima_actual(
        self,
        instancia_boton
    ):

        localidad = self.obtener_localidad()

        if localidad is None:
            return

        try:

            resultado = obtener_clima_actual(
                localidad
            )

            self.resultado_actual.text = (
                str(resultado)
            )

            self.mensaje.color = COLOR_EXITO

            self.mensaje.text = (
                f"Clima consultado para "
                f"{localidad}."
            )

        except Exception as error:

            self.mensaje.color = COLOR_ERROR

            self.mensaje.text = (
                "No fue posible consultar el clima."
            )

            self.resultado_actual.text = (
                f"Error: {error}"
            )

    # ========================================================
    # PRONÓSTICO
    # ========================================================

    def ver_pronostico(
        self,
        instancia_boton
    ):

        localidad = self.obtener_localidad()

        if localidad is None:
            return

        try:

            resultado = obtener_pronostico_dias(
                localidad
            )

            if isinstance(resultado, list):

                textos = []

                for dia in resultado:

                    textos.append(
                        str(dia)
                    )

                self.resultado_pronostico.text = (
                    "\n\n".join(textos)
                )

            else:

                self.resultado_pronostico.text = (
                    str(resultado)
                )

            self.mensaje.color = COLOR_EXITO

            self.mensaje.text = (
                f"Pronóstico consultado para "
                f"{localidad}."
            )

        except Exception as error:

            self.mensaje.color = COLOR_ERROR

            self.mensaje.text = (
                "No fue posible consultar "
                "el pronóstico."
            )

            self.resultado_pronostico.text = (
                f"Error: {error}"
            )


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

class AgroSmartApp(App):

    def build(self):

        self.title = "AgroSmart"

        return PantallaClima()


if __name__ == "__main__":

    AgroSmartApp().run()