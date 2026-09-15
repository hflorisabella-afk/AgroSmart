# app_principal.py
# Este archivo UNE las pantallas de los distintos módulos en una sola app,
# con una barra de botones arriba para moverse entre ellas.
#
# No repite ninguna lógica: importa las pantallas que ya existen
# (pantalla_cultivos.py, pantalla_clima.py, pantalla_riego.py) tal como están,
# y solo las organiza dentro de un ScreenManager (el "administrador de
# pantallas" de Kivy, que permite cambiar de una pantalla a otra).
#
# Este archivo va en Codigo/ (al mismo nivel que 'principal.py', 'modelos/',
# 'pantallas/' y 'riego/'), NO adentro de ninguna de esas carpetas.

import sys
import os

CARPETA_CODIGO = os.path.dirname(os.path.abspath(__file__))

# Le decimos a Python dónde buscar cada pantalla, ya que viven en carpetas distintas
sys.path.append(os.path.join(CARPETA_CODIGO, "pantallas"))
sys.path.append(os.path.join(CARPETA_CODIGO, "riego"))

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

# Importamos cada pantalla como un "módulo completo", para poder acceder
# tanto a su clase de pantalla como a su color de fondo (COLOR_FONDO)
import pantalla_cultivos
import pantalla_clima
import pantalla_riego


class ScreenCultivos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(pantalla_cultivos.PantallaCultivos())

    def on_enter(self):
        # Cada vez que se entra a esta pantalla, se aplica su color de fondo
        Window.clearcolor = pantalla_cultivos.COLOR_FONDO


class ScreenClima(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(pantalla_clima.PantallaClima())

    def on_enter(self):
        Window.clearcolor = pantalla_clima.COLOR_FONDO


class ScreenRiego(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(pantalla_riego.PantallaRiego())

    def on_enter(self):
        Window.clearcolor = pantalla_riego.COLOR_FONDO


def boton_de_navegacion(texto, color_fondo):
    return Button(
        text=texto,
        background_normal="",
        background_color=color_fondo,
        color=(1, 1, 1, 1),
        bold=True,
        font_size=15,
    )


class PantallaPrincipal(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # --- Barra de navegación (siempre visible arriba) ---
        barra = BoxLayout(orientation="horizontal", size_hint=(1, None), height=55, spacing=4, padding=4)

        boton_cultivos = boton_de_navegacion("Cultivos", pantalla_cultivos.COLOR_VERDE_PRINCIPAL)
        boton_cultivos.bind(on_press=lambda instancia: self.cambiar_pantalla("cultivos"))
        barra.add_widget(boton_cultivos)

        boton_clima = boton_de_navegacion(" Clima", pantalla_clima.COLOR_AZUL_BOTON)
        boton_clima.bind(on_press=lambda instancia: self.cambiar_pantalla("clima"))
        barra.add_widget(boton_clima)

        boton_riego = boton_de_navegacion("Riego", pantalla_riego.COLOR_AZUL_PRINCIPAL)
        boton_riego.bind(on_press=lambda instancia: self.cambiar_pantalla("riego"))
        barra.add_widget(boton_riego)

        self.add_widget(barra)

        # --- El "administrador de pantallas": guarda las 3 pantallas y muestra una a la vez ---
        self.manager = ScreenManager(transition=NoTransition())
        self.manager.add_widget(ScreenCultivos(name="cultivos"))
        self.manager.add_widget(ScreenClima(name="clima"))
        self.manager.add_widget(ScreenRiego(name="riego"))
        self.add_widget(self.manager)

    def cambiar_pantalla(self, nombre):
        self.manager.current = nombre


class AgroSmartApp(App):
    def build(self):
        self.title = "AgroSmart"
        Window.size = (800, 850)
        return PantallaPrincipal()


if __name__ == "__main__":
    AgroSmartApp().run()