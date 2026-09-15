# prueba_kivy.py


from kivy.app import App
from kivy.uix.label import Label


class PruebaApp(App):
    def build(self):
        # "build" es la función que Kivy llama para armar lo que se ve en pantalla.
        # Por ahora, solo mostramos un texto simple.
        return Label(text="¡Hola AgroSmart! Kivy está funcionando", font_size=24)


if __name__ == "__main__":
    PruebaApp().run()