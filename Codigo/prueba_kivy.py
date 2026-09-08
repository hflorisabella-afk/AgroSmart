# prueba_kivy.py
# Este archivo es SOLO una prueba, para confirmar que Kivy funciona en tu compu.
# No tiene nada que ver todavía con la lógica de cultivos.

from kivy.app import App
from kivy.uix.label import Label


class PruebaApp(App):
    def build(self):
        # "build" es la función que Kivy llama para armar lo que se ve en pantalla.
        # Por ahora, solo mostramos un texto simple.
        return Label(text="¡Hola AgroSmart! Kivy está funcionando 🌱", font_size=24)


if __name__ == "__main__":
    PruebaApp().run()