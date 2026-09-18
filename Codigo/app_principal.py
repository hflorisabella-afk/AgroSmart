# app_principal.py
# Este archivo UNE las pantallas de los distintos módulos en una sola app,
# con una barra de botones arriba para moverse entre ellas.
#
# Este archivo va en Codigo/ (al mismo nivel que 'principal.py',
# 'modelos/', 'pantallas/' y 'riego/').

import sys
import os

CARPETA_CODIGO = os.path.dirname(os.path.abspath(__file__))

# Le decimos a Python dónde buscar cada pantalla,
# ya que viven en carpetas distintas.
sys.path.append(
    os.path.join(CARPETA_CODIGO, "pantallas")
)

sys.path.append(
    os.path.join(CARPETA_CODIGO, "riego")
)


# ============================================================
# IMPORTACIONES DE KIVY
# ============================================================

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import (
    ScreenManager,
    Screen,
    NoTransition
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button


# ============================================================
# IMPORTAR PANTALLAS
# ============================================================

import pantalla_cultivos
import pantalla_clima
import pantalla_riego
import pantalla_calendario
import pantalla_inventario


# ============================================================
# PANTALLA CULTIVOS
# ============================================================

class ScreenCultivos(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.add_widget(
            pantalla_cultivos.PantallaCultivos()
        )

    def on_enter(self):

        Window.clearcolor = (
            pantalla_cultivos.COLOR_FONDO
        )


# ============================================================
# PANTALLA CLIMA
# ============================================================

class ScreenClima(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pantalla = (
            pantalla_clima.PantallaClima()
        )

        self.add_widget(
            self.pantalla
        )

    def on_enter(self):

        Window.clearcolor = (
            pantalla_clima.COLOR_FONDO
        )

        # Actualizar los cultivos cada vez
        # que entramos a Clima.
        self.pantalla.actualizar_lista()


# ============================================================
# PANTALLA RIEGO
# ============================================================

class ScreenRiego(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pantalla = (
            pantalla_riego.PantallaRiego()
        )

        self.add_widget(
            self.pantalla
        )

    def on_enter(self):

        Window.clearcolor = (
            pantalla_riego.COLOR_FONDO
        )

        # Actualizar los cultivos cada vez
        # que entramos a Riego.
        self.pantalla.actualizar_lista()


# ============================================================
# PANTALLA CALENDARIO
# ============================================================

class ScreenCalendario(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pantalla = (
            pantalla_calendario.PantallaCalendario()
        )

        self.add_widget(
            self.pantalla
        )

    def on_enter(self):

        Window.clearcolor = (
            pantalla_calendario.COLOR_FONDO
        )

        # Actualizar los cultivos cada vez
        # que entramos a Calendario.
        self.pantalla.actualizar_lista()


# ============================================================
# PANTALLA INVENTARIO
# ============================================================

class ScreenInventario(Screen):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.pantalla = (
            pantalla_inventario.PantallaInventario()
        )

        self.add_widget(
            self.pantalla
        )

    def on_enter(self):

        Window.clearcolor = (
            pantalla_inventario.COLOR_FONDO
        )

        # Actualizar el inventario cada vez
        # que entramos a esta pantalla.
        self.pantalla.actualizar_lista()


# ============================================================
# BOTÓN DE NAVEGACIÓN
# ============================================================

def boton_de_navegacion(
    texto,
    color_fondo
):

    return Button(
        text=texto,
        background_normal="",
        background_color=color_fondo,
        color=(1, 1, 1, 1),
        bold=True,
        font_size=15
    )


# ============================================================
# PANTALLA PRINCIPAL
# ============================================================

class PantallaPrincipal(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.orientation = "vertical"


        # ====================================================
        # BARRA DE NAVEGACIÓN
        # ====================================================

        barra = BoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=55,
            spacing=4,
            padding=4
        )


        # ----------------------------------------------------
        # CULTIVOS
        # ----------------------------------------------------

        boton_cultivos = boton_de_navegacion(
            "Cultivos",
            pantalla_cultivos.COLOR_VERDE_PRINCIPAL
        )

        boton_cultivos.bind(
            on_press=lambda instancia:
            self.cambiar_pantalla("cultivos")
        )

        barra.add_widget(
            boton_cultivos
        )


        # ----------------------------------------------------
        # CLIMA
        # ----------------------------------------------------

        boton_clima = boton_de_navegacion(
            "Clima",
            pantalla_clima.COLOR_AZUL_BOTON
        )

        boton_clima.bind(
            on_press=lambda instancia:
            self.cambiar_pantalla("clima")
        )

        barra.add_widget(
            boton_clima
        )


        # ----------------------------------------------------
        # RIEGO
        # ----------------------------------------------------

        boton_riego = boton_de_navegacion(
            "Riego",
            pantalla_riego.COLOR_AZUL_PRINCIPAL
        )

        boton_riego.bind(
            on_press=lambda instancia:
            self.cambiar_pantalla("riego")
        )

        barra.add_widget(
            boton_riego
        )


        # ----------------------------------------------------
        # CALENDARIO
        # ----------------------------------------------------

        boton_calendario = boton_de_navegacion(
            "Calendario",
            pantalla_calendario.COLOR_MORADO_PRINCIPAL
        )

        boton_calendario.bind(
            on_press=lambda instancia:
            self.cambiar_pantalla("calendario")
        )

        barra.add_widget(
            boton_calendario
        )


        # ----------------------------------------------------
        # INVENTARIO
        # ----------------------------------------------------

        boton_inventario = boton_de_navegacion(
            "Inventario",
            pantalla_inventario.COLOR_AMARILLO_PRINCIPAL
        )

        boton_inventario.bind(
            on_press=lambda instancia:
            self.cambiar_pantalla("inventario")
        )

        barra.add_widget(
            boton_inventario
        )


        # Agregar barra de navegación
        self.add_widget(
            barra
        )


        # ====================================================
        # ADMINISTRADOR DE PANTALLAS
        # ====================================================

        self.manager = ScreenManager(
            transition=NoTransition()
        )


        # ----------------------------------------------------
        # REGISTRAR TODAS LAS PANTALLAS
        # ----------------------------------------------------

        self.manager.add_widget(
            ScreenCultivos(
                name="cultivos"
            )
        )

        self.manager.add_widget(
            ScreenClima(
                name="clima"
            )
        )

        self.manager.add_widget(
            ScreenRiego(
                name="riego"
            )
        )

        self.manager.add_widget(
            ScreenCalendario(
                name="calendario"
            )
        )

        self.manager.add_widget(
            ScreenInventario(
                name="inventario"
            )
        )


        # Agregar administrador de pantallas
        self.add_widget(
            self.manager
        )


    # ========================================================
    # CAMBIAR DE PANTALLA
    # ========================================================

    def cambiar_pantalla(
        self,
        nombre
    ):

        self.manager.current = nombre


# ============================================================
# APLICACIÓN
# ============================================================

class AgroSmartApp(App):

    def build(self):

        self.title = "AgroSmart"

        Window.size = (
            800,
            850
        )

        return PantallaPrincipal()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    AgroSmartApp().run()