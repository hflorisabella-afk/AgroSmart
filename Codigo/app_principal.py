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
sys.path.append(os.path.join(CARPETA_CODIGO, "pantallas"))
sys.path.append(os.path.join(CARPETA_CODIGO, "riego"))


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
# PANTALLA GENÉRICA (sirve para todos los módulos)
# ============================================================

class ScreenModulo(Screen):

    def __init__(self, modulo, nombre_clase, **kwargs):

        super().__init__(**kwargs)

        self.modulo = modulo

        self.pantalla = getattr(modulo, nombre_clase)()

        self.add_widget(self.pantalla)

    def on_enter(self):

        Window.clearcolor = self.modulo.COLOR_FONDO

        # Actualizar los datos cada vez que entramos a la pantalla.
        if hasattr(self.pantalla, "actualizar_lista"):
            self.pantalla.actualizar_lista()


# ============================================================
# BOTÓN DE NAVEGACIÓN
# ============================================================

def boton_de_navegacion(texto, color_fondo):

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

        # (nombre interno, texto del botón, módulo, clase, color del botón)
        modulos = [
            ("cultivos", "Cultivos", pantalla_cultivos,
             "PantallaCultivos", pantalla_cultivos.COLOR_VERDE_PRINCIPAL),

            ("clima", "Clima", pantalla_clima,
             "PantallaClima", pantalla_clima.COLOR_AZUL_BOTON),

            ("riego", "Riego", pantalla_riego,
             "PantallaRiego", pantalla_riego.COLOR_AZUL_PRINCIPAL),

            ("calendario", "Calendario", pantalla_calendario,
             "PantallaCalendario", pantalla_calendario.COLOR_MORADO_PRINCIPAL),

            ("inventario", "Inventario", pantalla_inventario,
             "PantallaInventario", pantalla_inventario.COLOR_AMARILLO_PRINCIPAL),
        ]

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

        self.add_widget(barra)

        # ====================================================
        # ADMINISTRADOR DE PANTALLAS
        # ====================================================

        self.manager = ScreenManager(
            transition=NoTransition()
        )

        for nombre, texto, modulo, clase, color in modulos:

            boton = boton_de_navegacion(texto, color)

            boton.bind(
                on_press=lambda instancia, n=nombre:
                self.cambiar_pantalla(n)
            )

            barra.add_widget(boton)

            self.manager.add_widget(
                ScreenModulo(modulo, clase, name=nombre)
            )

        self.add_widget(self.manager)

    # ========================================================
    # CAMBIAR DE PANTALLA
    # ========================================================

    def cambiar_pantalla(self, nombre):

        self.manager.current = nombre


# ============================================================
# APLICACIÓN
# ============================================================

class AgroSmartApp(App):

    def build(self):

        self.title = "AgroSmart"

        Window.size = (800, 850)

        return PantallaPrincipal()


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    AgroSmartApp().run()