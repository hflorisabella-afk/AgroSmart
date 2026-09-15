# pantalla_riego.py
# Pantalla visual de AgroSmart para el módulo de Riego.
# Los cultivos se obtienen directamente desde GestorCultivos.
# No se registran cultivos nuevamente desde esta pantalla.

import sys
import os

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "modelos")
)

from gestor_cultivos import GestorCultivos

from riego_agrosmart import (
    GestorRiego,
    ControladorRiego,
    normalizar_codigo
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

COLOR_FONDO = (0.14, 0.07, 0.06, 1)

# Aunque el nombre se mantiene por compatibilidad con app_principal.py,
# este color es rojo/coral.
COLOR_AZUL_PRINCIPAL = (0.70, 0.30, 0.25, 1)

COLOR_ROJO_CLARO = (0.95, 0.60, 0.52, 1)

COLOR_TEXTO_CLARO = (0.95, 0.92, 0.90, 1)
COLOR_INFO = (0.65, 0.78, 0.88, 1)
COLOR_ERROR = (1, 0.45, 0.40, 1)
COLOR_EXITO = (0.55, 0.85, 0.55, 1)

COLOR_TARJETA = (0.25, 0.13, 0.11, 1)

# Compatibilidad con código anterior
COLOR_VERDE_PRINCIPAL = COLOR_AZUL_PRINCIPAL
COLOR_VERDE_CLARO = COLOR_ROJO_CLARO

Window.clearcolor = COLOR_FONDO
Window.size = (780, 850)


# ============================================================
# GESTORES COMPARTIDOS
# ============================================================

gestor_cultivos = GestorCultivos()

gestor_riego = GestorRiego(
    gestor_cultivos
)

controlador_riego = ControladorRiego(
    gestor_riego
)


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
# PANTALLA RIEGO
# ============================================================

class PantallaRiego(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

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
            text="AgroSmart - Control de Riego",
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
                "Selecciona un cultivo registrado para "
                "revisar su necesidad de riego."
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
            height=45,
            font_size=15,
            color=COLOR_INFO
        )

        contenido.add_widget(self.mensaje)

        # ----------------------------------------------------
        # BOTÓN REVISAR TODOS
        # ----------------------------------------------------

        boton_todos = boton_estilizado(
            "Revisar y regar todos los cultivos"
        )

        boton_todos.bind(
            on_press=self.revisar_y_regar_todos
        )

        contenido.add_widget(boton_todos)

        # ----------------------------------------------------
        # TÍTULO DE CULTIVOS
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

        # ----------------------------------------------------
        # LISTA
        # ----------------------------------------------------

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
        # RESULTADO
        # ----------------------------------------------------

        contenido.add_widget(
            Label(
                text="Resultado:",
                size_hint_y=None,
                height=35,
                font_size=17,
                color=COLOR_VERDE_CLARO,
                bold=True
            )
        )

        self.resultado = Label(
            text="Selecciona un cultivo.",
            size_hint_y=None,
            height=150,
            font_size=15,
            color=COLOR_TEXTO_CLARO,
            halign="left",
            valign="top"
        )

        self.resultado.bind(
            size=lambda inst, val:
            setattr(inst, "text_size", val)
        )

        contenido.add_widget(
            self.resultado
        )

        self.actualizar_lista()

    # ========================================================
    # ACTUALIZAR LISTA
    # ========================================================

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        # Volvemos a cargar la información del archivo
        # principal de cultivos.
        global gestor_cultivos
        gestor_cultivos = GestorCultivos()

        gestor_riego.gestor_cultivos = gestor_cultivos
        gestor_riego.sincronizar_con_cultivos()

        if len(gestor_cultivos.lista_cultivos) == 0:

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
        # CREAR BOTÓN POR CADA CULTIVO
        # ----------------------------------------------------

        for cultivo in gestor_cultivos.lista_cultivos:

            boton = Button(
                text=(
                    f"{cultivo.codigo} - "
                    f"{cultivo.nombre}\n"
                    f"{cultivo.tipo} | "
                    f"{cultivo.localidad} | "
                    f"Parcela {cultivo.numero_parcela}"
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
                self.revisar_cultivo(cultivo)
            )

            self.lista_cultivos.add_widget(
                boton
            )

    # ========================================================
    # REVISAR UN CULTIVO
    # ========================================================

    def revisar_cultivo(self, cultivo):

        resultado = controlador_riego.revisar_zona(
            cultivo.codigo
        )

        self.mostrar_resultado(
            cultivo,
            resultado
        )

    # ========================================================
    # REVISAR TODOS
    # ========================================================

    def revisar_y_regar_todos(
        self,
        instancia_boton
    ):

        resultados = (
            controlador_riego.revisar_y_regar_todas()
        )

        if not resultados:

            self.mensaje.color = COLOR_ERROR

            self.mensaje.text = (
                "No hay cultivos registrados."
            )

            self.resultado.text = ""

            return

        self.mensaje.color = COLOR_EXITO

        self.mensaje.text = (
            "Se revisaron todos los cultivos."
        )

        textos = []

        for resultado in resultados:

            nombre = resultado.get(
                "nombre",
                resultado.get(
                    "codigo",
                    ""
                )
            )

            estado = resultado.get(
                "estado",
                ""
            )

            mensaje = resultado.get(
                "mensaje",
                ""
            )

            textos.append(
                f"{nombre}\n"
                f"{mensaje}"
            )

        self.resultado.text = (
            "\n\n".join(textos)
        )

        self.actualizar_lista()

    # ========================================================
    # MOSTRAR RESULTADO
    # ========================================================

    def mostrar_resultado(
        self,
        cultivo,
        resultado
    ):

        estado = resultado.get(
            "estado",
            ""
        )

        mensaje = resultado.get(
            "mensaje",
            ""
        )

        humedad = resultado.get(
            "humedad",
            None
        )

        texto = (
            f"Cultivo: {cultivo.nombre}\n"
            f"Código: {cultivo.codigo}\n"
            f"Localidad: {cultivo.localidad}\n"
            f"Tierra: {cultivo.tipo_tierra}\n"
            f"Parcela: {cultivo.numero_parcela}\n"
        )

        if humedad is not None:

            texto += (
                f"Humedad actual: "
                f"{humedad}%\n"
            )

        texto += (
            f"\nEstado: {estado}\n"
            f"Recomendación: {mensaje}"
        )

        if "minutos" in resultado:

            texto += (
                f"\nDuración del riego: "
                f"{resultado['minutos']} minutos"
            )

        if "litros" in resultado:

            texto += (
                f"\nAgua estimada: "
                f"{resultado['litros']} litros"
            )

        if "probabilidad_lluvia" in resultado:

            texto += (
                f"\nProbabilidad de lluvia: "
                f"{resultado['probabilidad_lluvia']}%"
            )

        self.resultado.text = texto

        if estado == "regado":

            self.mensaje.color = COLOR_EXITO

        elif estado == "correcto":

            self.mensaje.color = COLOR_INFO

        elif estado == "lluvia":

            self.mensaje.color = COLOR_INFO

        else:

            self.mensaje.color = COLOR_ERROR

        self.mensaje.text = mensaje


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

class AgroSmartApp(App):

    def build(self):

        self.title = "AgroSmart"

        return PantallaRiego()


if __name__ == "__main__":

    AgroSmartApp().run()