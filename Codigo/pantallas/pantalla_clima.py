# pantalla_clima.py
# Pantalla visual de AgroSmart para el módulo de Clima y Alertas.
# Permite consultar el clima actual de una localidad, ver su alerta,
# y consultar el pronóstico de los próximos 5 días.
#
# La lógica real (consultar la API de Open-Meteo, calcular alertas) vive
# en modelos/clima.py — aquí solo conectamos eso con la pantalla.

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modelos"))

from clima import obtener_clima_actual, obtener_pronostico_dias

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# ================= COLORES DEL TEMA (igual que la pantalla de Cultivos) =================
COLOR_FONDO = (1, 1, 1, 1)
COLOR_VERDE_PRINCIPAL = (0.29, 0.49, 0.36, 1)
COLOR_VERDE_CLARO = (0.65, 0.85, 0.6, 1)
COLOR_TEXTO_CLARO = (0, 0, 0, 1)
COLOR_CAJA_TEXTO = (0.95, 0.97, 0.94, 1)
COLOR_ERROR = (1, 0.55, 0.5, 1)
COLOR_EXITO = (0.55, 0.9, 0.5, 1)
COLOR_INFO = (0, 0, 0, 1)

Window.clearcolor = COLOR_FONDO
Window.size = (750, 700)


def caja_de_texto(hint=""):
    return TextInput(
        multiline=False, hint_text=hint, font_size=17,
        padding=[10, 10, 10, 10], background_color=COLOR_CAJA_TEXTO,
        foreground_color=(0.1, 0.1, 0.1, 1), hint_text_color=(0.45, 0.45, 0.45, 1),
        size_hint=(0.6, 1),
    )


def boton_estilizado(texto, alto=45, color_fondo=None):
    return Button(
        text=texto, size_hint_y=None, height=alto, background_normal="",
        background_color=color_fondo if color_fondo else COLOR_VERDE_PRINCIPAL,
        color=(1, 1, 1, 1), bold=True,
    )


class PantallaClima(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        contenido = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=12)
        contenido.bind(minimum_height=contenido.setter("height"))
        self.add_widget(contenido)

        titulo = Label(text="AgroSmart - Clima y Alertas", font_size=24, bold=True,
                        size_hint_y=None, height=45, color=COLOR_VERDE_CLARO)
        contenido.add_widget(titulo)

        # --- Campo de localidad ---
        fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)
        etiqueta = Label(text="Localidad:", size_hint=(0.3, 1), font_size=16,
                          halign="right", valign="middle", color=COLOR_TEXTO_CLARO)
        etiqueta.bind(size=lambda inst, val: setattr(inst, "text_size", val))
        fila.add_widget(etiqueta)
        self.campo_localidad = caja_de_texto("ej: Chimaltenango")
        self.campo_localidad.size_hint = (0.7, 1)
        fila.add_widget(self.campo_localidad)
        contenido.add_widget(fila)

        # --- Botones ---
        fila_botones = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)
        boton_actual = boton_estilizado("Ver clima actual")
        boton_actual.bind(on_press=self.consultar_clima_actual)
        fila_botones.add_widget(boton_actual)

        boton_pronostico = boton_estilizado("Ver pronóstico (5 días)")
        boton_pronostico.bind(on_press=self.consultar_pronostico)
        fila_botones.add_widget(boton_pronostico)
        contenido.add_widget(fila_botones)

        # --- Mensaje de estado (cargando, error, etc.) ---
        self.mensaje = Label(text="", size_hint_y=None, height=30, color=COLOR_INFO)
        contenido.add_widget(self.mensaje)

        # --- Resultado: clima actual ---
        contenido.add_widget(Label(text="Clima actual:", size_hint_y=None, height=28,
                                    font_size=16, color=COLOR_VERDE_CLARO, bold=True))
        self.resultado_actual = Label(text="Todavía no se ha consultado nada.",
                                       size_hint_y=None, halign="left", valign="top",
                                       font_size=15, color=COLOR_TEXTO_CLARO)
        self.resultado_actual.bind(texture_size=self._actualizar_altura_resultado_actual)
        contenido.add_widget(self.resultado_actual)

        # --- Resultado: pronóstico ---
        contenido.add_widget(Label(text="Pronóstico de 5 días:", size_hint_y=None, height=28,
                                    font_size=16, color=COLOR_VERDE_CLARO, bold=True))
        self.resultado_pronostico = Label(text="", size_hint_y=None, halign="left", valign="top",
                                           font_size=14, color=COLOR_TEXTO_CLARO)
        self.resultado_pronostico.bind(texture_size=self._actualizar_altura_pronostico)
        contenido.add_widget(self.resultado_pronostico)

    def _actualizar_altura_resultado_actual(self, instancia, tamano):
        instancia.height = tamano[1]
        instancia.text_size = (instancia.width, None)

    def _actualizar_altura_pronostico(self, instancia, tamano):
        instancia.height = tamano[1]
        instancia.text_size = (instancia.width, None)

    def consultar_clima_actual(self, instancia_boton):
        localidad = self.campo_localidad.text.strip()
        if not localidad:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Escribe una localidad primero."
            return

        self.mensaje.color = COLOR_INFO
        self.mensaje.text = "Consultando clima... (necesita internet)"

        clima_actual = obtener_clima_actual(localidad)

        if clima_actual is None:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "No se pudo obtener el clima. Revisa tu conexión a internet o el nombre de la localidad."
            self.resultado_actual.text = "Sin datos."
            return

        self.mensaje.color = COLOR_EXITO
        self.mensaje.text = "Clima actualizado correctamente."
        self.resultado_actual.text = (
            f"{clima_actual}\n\n{clima_actual.generar_alerta()}\n\n"
            f"¿Necesita riego? {'Sí' if clima_actual.necesita_riego() else 'No'}"
        )

    def consultar_pronostico(self, instancia_boton):
        localidad = self.campo_localidad.text.strip()
        if not localidad:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Escribe una localidad primero."
            return

        self.mensaje.color = COLOR_INFO
        self.mensaje.text = "Consultando pronóstico... (necesita internet)"

        pronostico = obtener_pronostico_dias(localidad, dias=5)

        if not pronostico:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "No se pudo obtener el pronóstico. Revisa tu conexión a internet o el nombre de la localidad."
            self.resultado_pronostico.text = "Sin datos."
            return

        self.mensaje.color = COLOR_EXITO
        self.mensaje.text = "Pronóstico actualizado correctamente."

        lineas = []
        for clima_dia in pronostico:
            lineas.append(f"{clima_dia}\n   -> {clima_dia.generar_alerta()}")
        self.resultado_pronostico.text = "\n\n".join(lineas)


class AgroSmartClimaApp(App):
    def build(self):
        self.title = "AgroSmart - Clima"
        return PantallaClima()


if __name__ == "__main__":
    AgroSmartClimaApp().run()