from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock

import os
import sys

# ============================================================
# IMPORTAR MODELOS
# ============================================================

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "modelos")
)

from gestor_cultivos import GestorCultivos

# Importar funciones del módulo clima
sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "clima")
)

from clima import (
    obtener_clima_actual,
    obtener_pronostico_dias
)


# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = (0.08, 0.12, 0.18, 1)

COLOR_AZUL_PRINCIPAL = (0.30, 0.52, 0.72, 1)
COLOR_AZUL_CLARO = (0.65, 0.82, 0.95, 1)

COLOR_TEXTO = (0.94, 0.96, 0.98, 1)
COLOR_TEXTO_SECUNDARIO = (0.68, 0.74, 0.80, 1)

COLOR_TARJETA = (0.13, 0.20, 0.28, 1)
COLOR_TARJETA_CLARA = (0.19, 0.28, 0.38, 1)

COLOR_EXITO = (0.55, 0.85, 0.65, 1)
COLOR_ERROR = (1, 0.55, 0.50, 1)
COLOR_INFO = (0.55, 0.78, 0.95, 1)

# Compatibilidad con app_principal.py
COLOR_AZUL_BOTON = COLOR_AZUL_PRINCIPAL
COLOR_VERDE_PRINCIPAL = COLOR_AZUL_PRINCIPAL
COLOR_VERDE_CLARO = COLOR_AZUL_CLARO


# ============================================================
# GESTOR DE CULTIVOS
# ============================================================

gestor_cultivos = GestorCultivos()


# ============================================================
# BOTÓN REDONDEADO
# ============================================================

def boton_estilizado(
    texto,
    color=COLOR_AZUL_PRINCIPAL,
    altura=48
):

    boton = Button(
        text=texto,
        size_hint_y=None,
        height=dp(altura),
        background_normal="",
        background_down="",
        background_color=(0, 0, 0, 0),
        color=COLOR_TEXTO,
        bold=True
    )

    with boton.canvas.before:

        Color(*color)

        boton.rectangulo = RoundedRectangle(
            pos=boton.pos,
            size=boton.size,
            radius=[dp(12)]
        )

    def actualizar_fondo(instance, value):

        boton.rectangulo.pos = boton.pos
        boton.rectangulo.size = boton.size

    boton.bind(
        pos=actualizar_fondo,
        size=actualizar_fondo
    )

    return boton


# ============================================================
# TARJETA DE CULTIVO
# ============================================================

class TarjetaCultivo(BoxLayout):

    def __init__(self, cultivo, seleccionado=False, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(3),
            padding=[
                dp(18),
                dp(10),
                dp(18),
                dp(10)
            ],
            size_hint_y=None,
            height=dp(82),
            **kwargs
        )

        self.cultivo = cultivo

        # ----------------------------------------------------
        # FONDO
        # ----------------------------------------------------

        color_tarjeta = (
            COLOR_TARJETA_CLARA
            if seleccionado
            else COLOR_TARJETA
        )

        with self.canvas.before:

            Color(*color_tarjeta)

            self.rectangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ----------------------------------------------------
        # NOMBRE
        # ----------------------------------------------------

        nombre = Label(
            text=cultivo.nombre,
            color=COLOR_TEXTO,
            font_size="16sp",
            bold=True,
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle"
        )

        nombre.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.add_widget(nombre)

        # ----------------------------------------------------
        # INFORMACIÓN
        # ----------------------------------------------------

        informacion = Label(
            text=(
                f"{cultivo.tipo}  •  "
                f"{cultivo.localidad}  •  "
                f"Parcela {cultivo.numero_parcela}"
            ),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="13sp",
            size_hint_y=None,
            height=dp(25),
            halign="left",
            valign="middle"
        )

        informacion.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.add_widget(informacion)

    def actualizar_fondo(self, instance, value):

        self.rectangulo.pos = self.pos
        self.rectangulo.size = self.size


# ============================================================
# PANTALLA CLIMA
# ============================================================

class PantallaClima(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.do_scroll_x = False

        self.cultivo_seleccionado = None

        # ====================================================
        # CONTENEDOR PRINCIPAL
        # ====================================================

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[
                dp(20),
                dp(20),
                dp(20),
                dp(30)
            ],
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter(
                "height"
            )
        )

        self.add_widget(
            self.contenedor
        )

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = Label(
            text="CLIMA",
            color=COLOR_AZUL_CLARO,
            font_size="28sp",
            bold=True,
            size_hint_y=None,
            height=dp(45)
        )

        self.contenedor.add_widget(
            titulo
        )

        subtitulo = Label(
            text="Consulta el clima de tus cultivos",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="14sp",
            size_hint_y=None,
            height=dp(35)
        )

        self.contenedor.add_widget(
            subtitulo
        )

        # ====================================================
        # TUS CULTIVOS
        # ====================================================

        titulo_cultivos = Label(
            text="TUS CULTIVOS",
            color=COLOR_TEXTO,
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle"
        )

        titulo_cultivos.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(
            titulo_cultivos
        )

        # ----------------------------------------------------
        # LISTA DE CULTIVOS
        # ----------------------------------------------------

        self.lista_cultivos = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.contenedor.add_widget(
            self.lista_cultivos
        )

        # ====================================================
        # BOTONES DE CLIMA
        # ====================================================

        fila_botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(52)
        )

        self.boton_actual = boton_estilizado(
            "Clima actual"
        )

        self.boton_actual.bind(
            on_release=self.ver_clima_actual
        )

        self.boton_pronostico = boton_estilizado(
            "Pronóstico 5 días"
        )

        self.boton_pronostico.bind(
            on_release=self.ver_pronostico
        )

        fila_botones.add_widget(
            self.boton_actual
        )

        fila_botones.add_widget(
            self.boton_pronostico
        )

        self.contenedor.add_widget(
            fila_botones
        )

        # ====================================================
        # SEPARADOR
        # ====================================================

        separador = BoxLayout(
            size_hint_y=None,
            height=dp(2)
        )

        with separador.canvas.before:

            Color(*COLOR_AZUL_PRINCIPAL)

            separador.rectangulo = RoundedRectangle(
                pos=separador.pos,
                size=separador.size,
                radius=[dp(1)]
            )

        separador.bind(
            pos=lambda instance, value:
            setattr(
                separador.rectangulo,
                "pos",
                separador.pos
            ),
            size=lambda instance, value:
            setattr(
                separador.rectangulo,
                "size",
                separador.size
            )
        )

        self.contenedor.add_widget(
            separador
        )

        # ====================================================
        # INFORMACIÓN DEL CLIMA
        # ====================================================

        titulo_resultado = Label(
            text="INFORMACIÓN DEL CLIMA",
            color=COLOR_TEXTO,
            font_size="18sp",
            bold=True,
            size_hint_y=None,
            height=dp(45),
            halign="left",
            valign="middle"
        )

        titulo_resultado.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(
            titulo_resultado
        )

        # ----------------------------------------------------
        # CONTENEDOR DE RESULTADOS
        # ----------------------------------------------------

        self.resultado = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[
                dp(15),
                dp(15),
                dp(15),
                dp(15)
            ],
            size_hint_y=None,
            height=dp(260)
        )

        with self.resultado.canvas.before:

            Color(*COLOR_TARJETA)

            self.resultado.rectangulo = RoundedRectangle(
                pos=self.resultado.pos,
                size=self.resultado.size,
                radius=[dp(14)]
            )

        self.resultado.bind(
            pos=self.actualizar_fondo_resultado,
            size=self.actualizar_fondo_resultado
        )

        self.contenedor.add_widget(
            self.resultado
        )

        # ====================================================
        # MENSAJE INICIAL
        # ====================================================

        self.mostrar_mensaje(
            "Selecciona un cultivo para consultar el clima."
        )

        # Cargar cultivos
        Clock.schedule_once(
            lambda dt: self.actualizar_lista(),
            0
        )

    # ========================================================
    # ACTUALIZAR FONDO RESULTADO
    # ========================================================

    def actualizar_fondo_resultado(
        self,
        instance,
        value
    ):

        self.resultado.rectangulo.pos = (
            self.resultado.pos
        )

        self.resultado.rectangulo.size = (
            self.resultado.size
        )

    # ========================================================
    # ACTUALIZAR LISTA
    # ========================================================

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        # Crear nuevamente el gestor para obtener
        # los cultivos guardados actualmente.
        gestor = GestorCultivos()

        cultivos = gestor.lista_cultivos

        # ----------------------------------------------------
        # SI NO HAY CULTIVOS
        # ----------------------------------------------------

        if not cultivos:

            mensaje = Label(
                text=(
                    "No hay cultivos registrados "
                    "todavía."
                ),
                color=COLOR_TEXTO_SECUNDARIO,
                font_size="14sp",
                size_hint_y=None,
                height=dp(60),
                halign="center",
                valign="middle"
            )

            mensaje.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.lista_cultivos.add_widget(
                mensaje
            )

            self.lista_cultivos.height = dp(60)

            return

        # ====================================================
        # CREAR TARJETAS
        # ====================================================

        for cultivo in cultivos:

            tarjeta = TarjetaCultivo(
                cultivo,
                seleccionado=(
                    self.cultivo_seleccionado is not None
                    and
                    self.cultivo_seleccionado.codigo
                    == cultivo.codigo
                )
            )

            # Toda la tarjeta es seleccionable
            tarjeta.bind(
                on_touch_up=lambda instance, touch,
                cultivo=cultivo:
                self.seleccionar_desde_touch(
                    instance,
                    touch,
                    cultivo
                )
            )

            self.lista_cultivos.add_widget(
                tarjeta
            )

        # Altura explícita para que las tarjetas
        # no se superpongan.
        cantidad = len(cultivos)

        self.lista_cultivos.height = (
            cantidad * dp(82)
            +
            max(0, cantidad - 1) * dp(10)
        )

        self.contenedor.do_layout()

    # ========================================================
    # SELECCIONAR CULTIVO DESDE TARJETA
    # ========================================================

    def seleccionar_desde_touch(
        self,
        instance,
        touch,
        cultivo
    ):

        if instance.collide_point(
            *touch.pos
        ):

            self.seleccionar_cultivo(
                cultivo
            )

            return True

        return False

    # ========================================================
    # SELECCIONAR CULTIVO
    # ========================================================

    def seleccionar_cultivo(
        self,
        cultivo
    ):

        self.cultivo_seleccionado = cultivo

        self.mostrar_mensaje(
            (
                f"Cultivo seleccionado: "
                f"{cultivo.nombre}\n"
                f"Localidad: {cultivo.localidad}"
            )
        )

        self.actualizar_lista()

    # ========================================================
    # OBTENER LOCALIDAD
    # ========================================================

    def obtener_localidad(self):

        if self.cultivo_seleccionado is None:

            return None

        return (
            self.cultivo_seleccionado.localidad
        )

    # ========================================================
    # CLIMA ACTUAL
    # ========================================================

    def ver_clima_actual(self, instance):

        if self.cultivo_seleccionado is None:

            self.mostrar_mensaje(
                "Primero selecciona un cultivo."
            )

            return

        localidad = self.obtener_localidad()

        if not localidad:

            self.mostrar_mensaje(
                "El cultivo no tiene localidad."
            )

            return

        self.mostrar_mensaje(
            "Consultando clima actual..."
        )

        try:

            clima = obtener_clima_actual(
                localidad
            )

            self.mostrar_clima_actual(
                clima
            )

        except Exception as error:

            self.mostrar_error(
                f"No se pudo obtener el clima:\n"
                f"{error}"
            )

    # ========================================================
    # MOSTRAR CLIMA ACTUAL
    # ========================================================

    def mostrar_clima_actual(
        self,
        clima
    ):

        self.resultado.clear_widgets()

        if clima is None:

            self.mostrar_error(
                "No se pudo obtener el clima."
            )

            return

        # ====================================================
        # LOCALIDAD
        # ====================================================

        localidad = Label(
            text=f"Localidad: {clima.localidad}",
            color=COLOR_AZUL_CLARO,
            font_size="19sp",
            bold=True,
            size_hint_y=None,
            height=dp(38),
            halign="left",
            valign="middle"
        )

        localidad.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            localidad
        )

        # ====================================================
        # TEMPERATURA
        # ====================================================

        temperatura = Label(
            text=(
                f"Temperatura: "
                f"{clima.temperatura} °C"
            ),
            color=COLOR_TEXTO,
            font_size="17sp",
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle"
        )

        temperatura.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            temperatura
        )

        # ====================================================
        # LLUVIA
        # ====================================================

        lluvia = Label(
            text=(
                f"Probabilidad de lluvia: "
                f"{clima.probabilidad_lluvia}%"
            ),
            color=COLOR_TEXTO,
            font_size="16sp",
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle"
        )

        lluvia.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            lluvia
        )

        # ====================================================
        # DESCRIPCIÓN
        # ====================================================

        descripcion = Label(
            text=(
                f"Condición: "
                f"{clima.descripcion}"
            ),
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="15sp",
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle"
        )

        descripcion.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            descripcion
        )

        # ====================================================
        # ALERTA
        # ====================================================

        alerta = clima.generar_alerta()

        texto_alerta = Label(
            text=alerta,
            color=(
                COLOR_ERROR
                if "Alerta" in alerta
                else COLOR_EXITO
            ),
            font_size="14sp",
            size_hint_y=None,
            height=dp(55),
            halign="left",
            valign="middle"
        )

        texto_alerta.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            texto_alerta
        )

    # ========================================================
    # PRONÓSTICO
    # ========================================================

    def ver_pronostico(self, instance):

        if self.cultivo_seleccionado is None:

            self.mostrar_mensaje(
                "Primero selecciona un cultivo."
            )

            return

        localidad = self.obtener_localidad()

        if not localidad:

            self.mostrar_mensaje(
                "El cultivo no tiene localidad."
            )

            return

        self.mostrar_mensaje(
            "Consultando pronóstico de 5 días..."
        )

        try:

            pronostico = obtener_pronostico_dias(
                localidad,
                5
            )

            self.mostrar_pronostico(
                pronostico
            )

        except Exception as error:

            self.mostrar_error(
                f"No se pudo obtener el pronóstico:\n"
                f"{error}"
            )

    # ========================================================
    # MOSTRAR PRONÓSTICO
    # ========================================================

    def mostrar_pronostico(
        self,
        pronostico
    ):

        self.resultado.clear_widgets()

        if not pronostico:

            self.mostrar_error(
                "No se pudo obtener el pronóstico."
            )

            return

        # ----------------------------------------------------
        # ALTURA SEGÚN CANTIDAD DE DÍAS
        # ----------------------------------------------------

        cantidad = len(pronostico)

        altura = (
            dp(20)
            +
            cantidad * dp(48)
            +
            max(0, cantidad - 1) * dp(5)
            +
            dp(20)
        )

        self.resultado.height = max(
            dp(260),
            altura
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        titulo = Label(
            text=(
                f"Pronóstico para "
                f"{self.cultivo_seleccionado.localidad}"
            ),
            color=COLOR_AZUL_CLARO,
            font_size="17sp",
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign="left",
            valign="middle"
        )

        titulo.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            titulo
        )

        # ----------------------------------------------------
        # DÍAS
        # ----------------------------------------------------

        for clima in pronostico:

            dia = Label(
                text=(
                    f"{clima.localidad}  |  "
                    f"{clima.temperatura} °C  |  "
                    f"Lluvia: "
                    f"{clima.probabilidad_lluvia}%  |  "
                    f"{clima.descripcion}"
                ),
                color=COLOR_TEXTO,
                font_size="13sp",
                size_hint_y=None,
                height=dp(48),
                halign="left",
                valign="middle"
            )

            dia.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            self.resultado.add_widget(
                dia
            )

    # ========================================================
    # MOSTRAR MENSAJE
    # ========================================================

    def mostrar_mensaje(
        self,
        texto
    ):

        self.resultado.clear_widgets()

        self.resultado.height = dp(260)

        mensaje = Label(
            text=texto,
            color=COLOR_INFO,
            font_size="15sp",
            halign="center",
            valign="middle"
        )

        mensaje.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            mensaje
        )

    # ========================================================
    # MOSTRAR ERROR
    # ========================================================

    def mostrar_error(
        self,
        texto
    ):

        self.resultado.clear_widgets()

        self.resultado.height = dp(260)

        mensaje = Label(
            text=texto,
            color=COLOR_ERROR,
            font_size="15sp",
            halign="center",
            valign="middle"
        )

        mensaje.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.resultado.add_widget(
            mensaje
        )


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

if __name__ == "__main__":

    from kivy.app import App

    class PruebaClima(App):

        def build(self):

            return PantallaClima()

    PruebaClima().run()