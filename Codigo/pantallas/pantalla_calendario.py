from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock

from datetime import datetime

import sys
import os


# =========================================================
# RUTAS
# =========================================================

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "modelos"
    )
)

from gestor_cultivos import GestorCultivos
from calendario import GestorCalendario, EventoCalendario
from fechas import normalizar_fecha


# =========================================================
# COLORES
# =========================================================

COLOR_FONDO = (0, 0, 0, 1)

COLOR_MORADO = (0.48, 0.32, 0.68, 1)

COLOR_MORADO_PRINCIPAL = COLOR_MORADO

COLOR_MORADO_BOTON = (0.58, 0.40, 0.78, 1)

COLOR_MORADO_CLARO = (0.82, 0.74, 0.94, 1)

COLOR_TEXTO = (0.8, 0.8, 0.8, 1)

COLOR_TEXTO_SECUNDARIO = (0.65, 0.62, 0.72, 1)

COLOR_TARJETA = (0.105, 0.08, 0.15, 1)

COLOR_TARJETA_CLARA = (0.15, 0.115, 0.21, 1)

COLOR_TARJETA_SELECCIONADA = (0.22, 0.15, 0.31, 1)

COLOR_BORDE = (0.29, 0.21, 0.39, 1)

COLOR_VERDE = (0.43, 0.82, 0.57, 1)

COLOR_AZUL = (0.45, 0.68, 0.92, 1)

COLOR_ROJO = (0.92, 0.43, 0.45, 1)

COLOR_BLANCO = (1, 1, 1, 1)


# =========================================================
# FONDO DE TARJETAS
# =========================================================

def agregar_fondo(widget, color, radio=18, borde=False):

    with widget.canvas.before:

        Color(*color)

        rect = RoundedRectangle(
            pos=widget.pos,
            size=widget.size,
            radius=[dp(radio)]
        )

        widget.bind(
            pos=lambda instancia, valor:
            setattr(rect, "pos", valor)
        )

        widget.bind(
            size=lambda instancia, valor:
            setattr(rect, "size", valor)
        )

        if borde:

            Color(*COLOR_BORDE)

            linea = Line(
                rounded_rectangle=(
                    widget.x,
                    widget.y,
                    widget.width,
                    widget.height,
                    dp(radio)
                ),
                width=1
            )

            widget.bind(
                pos=lambda instancia, valor:
                setattr(
                    linea,
                    "rounded_rectangle",
                    (
                        instancia.x,
                        instancia.y,
                        instancia.width,
                        instancia.height,
                        dp(radio)
                    )
                )
            )

            widget.bind(
                size=lambda instancia, valor:
                setattr(
                    linea,
                    "rounded_rectangle",
                    (
                        instancia.x,
                        instancia.y,
                        instancia.width,
                        instancia.height,
                        dp(radio)
                    )
                )
            )


# =========================================================
# PANTALLA CALENDARIO
# =========================================================

class PantallaCalendario(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.do_scroll_x = False
        self.bar_width = dp(4)

        # -------------------------------------------------
        # GESTORES
        # -------------------------------------------------

        self.gestor_cultivos = GestorCultivos()

        self.gestor_calendario = GestorCalendario()

        self.cultivo_seleccionado = None

        self.tarjetas_cultivos = {}

        # -------------------------------------------------
        # CONTENEDOR PRINCIPAL
        # -------------------------------------------------

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(18),
            padding=[
                dp(18),
                dp(20),
                dp(18),
                dp(30)
            ],
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        self.add_widget(self.contenedor)

        # -------------------------------------------------
        # CREAR INTERFAZ
        # -------------------------------------------------

        self.crear_interfaz()

        self.actualizar_lista()


    # =====================================================
    # INTERFAZ
    # =====================================================

    def crear_interfaz(self):

        # -------------------------------------------------
        # ENCABEZADO
        # -------------------------------------------------

        encabezado = BoxLayout(
            orientation="vertical",
            spacing=dp(3),
            size_hint_y=None,
            height=dp(72)
        )

        titulo = Label(
            text="Calendario",
            font_size="30sp",
            bold=True,
            color=COLOR_TEXTO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(42)
        )

        titulo.bind(
            size=lambda instancia, valor:
            setattr(instancia, "text_size", valor)
        )

        subtitulo = Label(
            text="Organiza tus actividades y controla tus cosechas",
            font_size="13sp",
            color=COLOR_TEXTO_SECUNDARIO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(25)
        )

        subtitulo.bind(
            size=lambda instancia, valor:
            setattr(instancia, "text_size", valor)
        )

        encabezado.add_widget(titulo)
        encabezado.add_widget(subtitulo)

        self.contenedor.add_widget(encabezado)

        # -------------------------------------------------
        # TUS CULTIVOS
        # -------------------------------------------------

        self.contenedor.add_widget(
            self.crear_titulo_seccion("TUS CULTIVOS")
        )

        self.lista_cultivos = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.contenedor.add_widget(
            self.lista_cultivos
        )

        # -------------------------------------------------
        # PRÓXIMA COSECHA
        # -------------------------------------------------

        self.contenedor.add_widget(
            self.crear_titulo_seccion("PRÓXIMA COSECHA")
        )

        self.tarjeta_prediccion = BoxLayout(
            orientation="vertical",
            spacing=dp(4),
            padding=[
                dp(20),
                dp(15)
            ],
            size_hint_y=None,
            height=dp(155)
        )

        agregar_fondo(
            self.tarjeta_prediccion,
            COLOR_TARJETA_CLARA,
            20,
            True
        )

        self.label_prediccion = Label(
            text="Selecciona un cultivo para ver su predicción.",
            font_size="14sp",
            color=COLOR_TEXTO_SECUNDARIO,
            halign="left",
            valign="middle"
        )

        self.label_prediccion.bind(
            size=lambda instancia, valor:
            setattr(instancia, "text_size", valor)
        )

        self.tarjeta_prediccion.add_widget(
            self.label_prediccion
        )

        self.contenedor.add_widget(
            self.tarjeta_prediccion
        )

        # -------------------------------------------------
        # BOTÓN AGREGAR ACTIVIDAD
        # -------------------------------------------------

        self.boton_agregar = Button(
            text="+   Agregar actividad",
            size_hint_y=None,
            height=dp(56),
            background_normal="",
            background_down="",
            background_color=(0, 0, 0, 0),
            color=COLOR_BLANCO,
            font_size="15sp",
            bold=True
        )

        agregar_fondo(
            self.boton_agregar,
            COLOR_MORADO_BOTON,
            16
        )

        self.boton_agregar.bind(
            on_release=self.mostrar_popup_tipo_actividad
        )

        self.contenedor.add_widget(
            self.boton_agregar
        )

        # -------------------------------------------------
        # SEPARADOR
        # -------------------------------------------------

        separador = BoxLayout(
            size_hint_y=None,
            height=dp(2)
        )

        self.contenedor.add_widget(
            separador
        )

        # -------------------------------------------------
        # PRÓXIMAS ACTIVIDADES
        # -------------------------------------------------

        self.contenedor.add_widget(
            self.crear_titulo_seccion(
                "PRÓXIMAS ACTIVIDADES"
            )
        )

        self.lista_eventos = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.contenedor.add_widget(
            self.lista_eventos
        )


    # =====================================================
    # TÍTULO DE SECCIÓN
    # =====================================================

    def crear_titulo_seccion(self, texto):

        contenedor = BoxLayout(
            size_hint_y=None,
            height=dp(28)
        )

        label = Label(
            text=texto,
            font_size="11sp",
            bold=True,
            color=COLOR_MORADO_CLARO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28)
        )

        label.bind(
            size=lambda instancia, valor:
            setattr(instancia, "text_size", valor)
        )

        contenedor.add_widget(label)

        return contenedor


    # =====================================================
    # ACTUALIZAR CULTIVOS
    # =====================================================

    def actualizar_lista(self, *args):

        self.gestor_cultivos = GestorCultivos()

        self.lista_cultivos.clear_widgets()

        self.tarjetas_cultivos.clear()

        self.cultivo_seleccionado = None

        # -------------------------------------------------
        # NO HAY CULTIVOS
        # -------------------------------------------------

        if not self.gestor_cultivos.lista_cultivos:

            mensaje = Label(
                text="Todavía no tienes cultivos registrados.",
                font_size="14sp",
                color=COLOR_TEXTO_SECUNDARIO,
                size_hint_y=None,
                height=dp(60),
                halign="center",
                valign="middle"
            )

            mensaje.bind(
                size=lambda instancia, valor:
                setattr(instancia, "text_size", valor)
            )

            self.lista_cultivos.add_widget(
                mensaje
            )

            self.lista_cultivos.height = dp(60)

            self.label_prediccion.text = (
                "Registra un cultivo para comenzar."
            )

            self.actualizar_eventos()

            Clock.schedule_once(
                lambda dt: self.actualizar_alturas(),
                0
            )

            return

        # -------------------------------------------------
        # MOSTRAR CULTIVOS
        # -------------------------------------------------

        for cultivo in self.gestor_cultivos.lista_cultivos:

            tarjeta = self.crear_tarjeta_cultivo(
                cultivo
            )

            self.lista_cultivos.add_widget(
                tarjeta
            )

            self.tarjetas_cultivos[
                cultivo.codigo
            ] = tarjeta

        # Altura explícita para evitar que Kivy
        # comprima las tarjetas
        cantidad = len(
            self.gestor_cultivos.lista_cultivos
        )

        self.lista_cultivos.height = (
            cantidad * dp(88)
            + max(0, cantidad - 1) * dp(10)
        )

        self.actualizar_eventos()

        Clock.schedule_once(
            lambda dt: self.actualizar_alturas(),
            0
        )


    # =====================================================
    # TARJETA CULTIVO
    # =====================================================

    def crear_tarjeta_cultivo(self, cultivo):

        tarjeta = BoxLayout(
            orientation="vertical",
            spacing=dp(1),
            padding=[
                dp(18),
                dp(8)
            ],
            size_hint_y=None,
            height=dp(88)
        )

        agregar_fondo(
            tarjeta,
            COLOR_TARJETA,
            18,
            True
        )

        # -------------------------------------------------
        # NOMBRE
        # -------------------------------------------------

        nombre = Label(
            text=str(cultivo.nombre).upper(),
            font_size="16sp",
            bold=True,
            color=COLOR_TEXTO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(27)
        )

        nombre.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # DETALLES
        # -------------------------------------------------

        detalles = Label(
            text=(
                f"{cultivo.tipo}   ·   "
                f"Parcela {cultivo.numero_parcela}"
            ),
            font_size="12sp",
            color=COLOR_TEXTO_SECUNDARIO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(21)
        )

        detalles.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # LOCALIDAD
        # -------------------------------------------------

        localidad = Label(
            text=f"●  {cultivo.localidad}",
            font_size="11sp",
            color=COLOR_MORADO_CLARO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22)
        )

        localidad.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        tarjeta.add_widget(nombre)
        tarjeta.add_widget(detalles)
        tarjeta.add_widget(localidad)

        # -------------------------------------------------
        # DETECTAR CLIC
        # -------------------------------------------------

        def tocar_tarjeta(instancia, touch):

            if instancia.collide_point(
                *touch.pos
            ):

                self.seleccionar_cultivo(
                    cultivo,
                    tarjeta
                )

                return True

            return False

        tarjeta.bind(
            on_touch_down=tocar_tarjeta
        )

        return tarjeta


    # =====================================================
    # SELECCIONAR CULTIVO
    # =====================================================

    def seleccionar_cultivo(
        self,
        cultivo,
        tarjeta=None
    ):

        self.cultivo_seleccionado = cultivo

        # -------------------------------------------------
        # ACTUALIZAR FONDO DE TARJETAS
        # -------------------------------------------------

        for codigo, tarjeta_actual in (
            self.tarjetas_cultivos.items()
        ):

            if codigo == cultivo.codigo:

                color = COLOR_TARJETA_SELECCIONADA

            else:

                color = COLOR_TARJETA

            # Se agrega un nuevo fondo únicamente
            # para actualizar la apariencia.
            agregar_fondo(
                tarjeta_actual,
                color,
                18,
                True
            )

        # -------------------------------------------------
        # PREDICCIÓN
        # -------------------------------------------------

        try:

            prediccion = (
                self.gestor_calendario
                .calcular_prediccion(
                    cultivo.codigo,
                    cultivo.tipo,
                    cultivo.fecha_siembra
                )
            )

            self.mostrar_prediccion(
                cultivo,
                prediccion
            )

        except ValueError as error:

            self.label_prediccion.text = str(
                error
            )

        # -------------------------------------------------
        # EVENTOS
        # -------------------------------------------------

        self.actualizar_eventos()

        Clock.schedule_once(
            lambda dt: self.actualizar_alturas(),
            0
        )


    # =====================================================
    # MOSTRAR PREDICCIÓN
    # =====================================================

    def mostrar_prediccion(
        self,
        cultivo,
        prediccion
    ):

        if prediccion.estado == "En crecimiento":

            estado_color = COLOR_AZUL

        elif prediccion.estado == "Próximo a cosechar":

            estado_color = COLOR_VERDE

        else:

            estado_color = COLOR_ROJO

        self.tarjeta_prediccion.clear_widgets()

        # -------------------------------------------------
        # CULTIVO
        # -------------------------------------------------

        titulo = Label(
            text=str(cultivo.nombre).upper(),
            font_size="13sp",
            bold=True,
            color=COLOR_MORADO_CLARO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22)
        )

        titulo.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # ETIQUETA
        # -------------------------------------------------

        etiqueta = Label(
            text="COSECHA ESTIMADA",
            font_size="10sp",
            color=COLOR_TEXTO_SECUNDARIO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(18)
        )

        etiqueta.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = Label(
            text=str(prediccion.fecha_estimada),
            font_size="27sp",
            bold=True,
            color=COLOR_TEXTO,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(42)
        )

        fecha.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # ESTADO
        # -------------------------------------------------

        estado = Label(
            text=(
                f"{prediccion.dias_restantes} días restantes"
                f"   ·   {prediccion.estado}"
            ),
            font_size="12sp",
            color=estado_color,
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(28)
        )

        estado.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        self.tarjeta_prediccion.add_widget(
            titulo
        )

        self.tarjeta_prediccion.add_widget(
            etiqueta
        )

        self.tarjeta_prediccion.add_widget(
            fecha
        )

        self.tarjeta_prediccion.add_widget(
            estado
        )


    # =====================================================
    # ACTUALIZAR EVENTOS
    # =====================================================

    def actualizar_eventos(self):

        self.lista_eventos.clear_widgets()

        # El árbol binario ya entrega los eventos ordenados por fecha
        eventos = self.gestor_calendario.eventos_ordenados()

        # -------------------------------------------------
        # FILTRAR POR CULTIVO
        # -------------------------------------------------

        if self.cultivo_seleccionado:

            eventos = [
                evento
                for evento in eventos
                if evento.codigo_cultivo
                ==
                self.cultivo_seleccionado.codigo
            ]

        # -------------------------------------------------
        # NO HAY EVENTOS
        # -------------------------------------------------

        if not eventos:

            if self.cultivo_seleccionado:

                texto = (
                    "No hay actividades programadas "
                    "para este cultivo."
                )

            else:

                texto = (
                    "Selecciona un cultivo para "
                    "ver sus actividades."
                )

            mensaje = Label(
                text=texto,
                font_size="13sp",
                color=COLOR_TEXTO_SECUNDARIO,
                size_hint_y=None,
                height=dp(55),
                halign="center",
                valign="middle"
            )

            mensaje.bind(
                size=lambda instancia, valor:
                setattr(
                    instancia,
                    "text_size",
                    valor
                )
            )

            self.lista_eventos.add_widget(
                mensaje
            )

            self.lista_eventos.height = dp(55)

            return

        # -------------------------------------------------
        # MOSTRAR EVENTOS
        # -------------------------------------------------

        for evento in eventos:

            tarjeta = self.crear_tarjeta_evento(
                evento
            )

            self.lista_eventos.add_widget(
                tarjeta
            )

        # Altura explícita
        cantidad = len(eventos)

        self.lista_eventos.height = (
            cantidad * dp(78)
            + max(0, cantidad - 1) * dp(10)
        )

        Clock.schedule_once(
            lambda dt: self.actualizar_alturas(),
            0
        )


    # =====================================================
    # TARJETA EVENTO
    # =====================================================

    def crear_tarjeta_evento(self, evento):

        tarjeta = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            padding=[
                dp(16),
                dp(10)
            ],
            size_hint_y=None,
            height=dp(78)
        )

        agregar_fondo(
            tarjeta,
            COLOR_TARJETA,
            16,
            True
        )

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = Label(
            text=str(evento.fecha),
            font_size="12sp",
            bold=True,
            color=COLOR_MORADO_CLARO,
            size_hint_x=0.30,
            size_hint_y=1,
            halign="center",
            valign="middle"
        )

        fecha.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # CONTENIDO
        # -------------------------------------------------

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(2),
            size_hint_y=1
        )

        # -------------------------------------------------
        # TIPO
        # -------------------------------------------------

        tipo = Label(
            text=str(evento.tipo),
            font_size="14sp",
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(25),
            halign="left",
            valign="middle"
        )

        tipo.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        # -------------------------------------------------
        # DESCRIPCIÓN
        # -------------------------------------------------

        descripcion = Label(
            text=(
                str(evento.descripcion)
                if evento.descripcion
                else "Sin descripción"
            ),
            font_size="11sp",
            color=COLOR_TEXTO_SECUNDARIO,
            size_hint_y=None,
            height=dp(30),
            halign="left",
            valign="middle"
        )

        descripcion.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        contenido.add_widget(tipo)
        contenido.add_widget(descripcion)

        tarjeta.add_widget(fecha)
        tarjeta.add_widget(contenido)

        return tarjeta


    # =====================================================
    # POPUP TIPO DE ACTIVIDAD
    # =====================================================

    def mostrar_popup_tipo_actividad(self, *args):

        if not self.cultivo_seleccionado:

            self.mostrar_mensaje(
                "Selecciona primero un cultivo."
            )

            return

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(18)
        )

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------

        titulo = Label(
            text="Agregar actividad",
            font_size="20sp",
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(38)
        )

        # -------------------------------------------------
        # SUBTÍTULO
        # -------------------------------------------------

        subtitulo = Label(
            text=(
                "Selecciona una actividad para "
                f"{self.cultivo_seleccionado.nombre}"
            ),
            font_size="12sp",
            color=COLOR_TEXTO_SECUNDARIO,
            size_hint_y=None,
            height=dp(35),
            halign="center",
            valign="middle"
        )

        subtitulo.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        contenido.add_widget(titulo)
        contenido.add_widget(subtitulo)

        # -------------------------------------------------
        # TIPOS DE ACTIVIDAD
        # -------------------------------------------------

        actividades = [
            "Siembra",
            "Riego",
            "Fertilización",
            "Cosecha",
            "Control de plagas",
            "Poda",
            "Otra actividad"
        ]

        popup = Popup(
            title="",
            content=contenido,
            size_hint=(0.88, None),
            height=dp(470),
            separator_color=COLOR_MORADO
        )

        for actividad in actividades:

            boton = Button(
                text=actividad,
                size_hint_y=None,
                height=dp(45),
                background_normal="",
                background_down="",
                background_color=COLOR_TARJETA_CLARA,
                color=COLOR_TEXTO,
                font_size="13sp"
            )

            boton.bind(
                on_release=lambda instancia,
                actividad=actividad:
                self.seleccionar_tipo_actividad(
                    popup,
                    actividad
                )
            )

            contenido.add_widget(
                boton
            )

        popup.open()


    # =====================================================
    # SELECCIONAR ACTIVIDAD
    # =====================================================

    def seleccionar_tipo_actividad(
        self,
        popup,
        actividad
    ):

        popup.dismiss()

        self.mostrar_popup_datos_evento(
            actividad
        )


    # =====================================================
    # DATOS DEL EVENTO
    # =====================================================

    def mostrar_popup_datos_evento(
        self,
        actividad
    ):

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(18)
        )

        # -------------------------------------------------
        # TÍTULO
        # -------------------------------------------------

        titulo = Label(
            text=actividad,
            font_size="20sp",
            bold=True,
            color=COLOR_TEXTO,
            size_hint_y=None,
            height=dp(35)
        )

        # -------------------------------------------------
        # CULTIVO
        # -------------------------------------------------

        cultivo = Label(
            text=(
                "Cultivo: "
                f"{self.cultivo_seleccionado.nombre}"
            ),
            font_size="12sp",
            color=COLOR_TEXTO_SECUNDARIO,
            size_hint_y=None,
            height=dp(25)
        )

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = TextInput(
            hint_text="Fecha (YYYY-MM-DD)",
            text=datetime.now().strftime(
                "%Y-%m-%d"
            ),
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=COLOR_TARJETA_CLARA,
            foreground_color=COLOR_TEXTO,
            hint_text_color=COLOR_TEXTO_SECUNDARIO
        )

        # -------------------------------------------------
        # DESCRIPCIÓN
        # -------------------------------------------------

        descripcion = TextInput(
            hint_text="Descripción de la actividad",
            multiline=True,
            size_hint_y=None,
            height=dp(80),
            background_normal="",
            background_color=COLOR_TARJETA_CLARA,
            foreground_color=COLOR_TEXTO,
            hint_text_color=COLOR_TEXTO_SECUNDARIO
        )

        # -------------------------------------------------
        # BOTONES
        # -------------------------------------------------

        botones = BoxLayout(
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )

        cancelar = Button(
            text="Cancelar",
            background_normal="",
            background_color=COLOR_TARJETA_CLARA,
            color=COLOR_TEXTO
        )

        guardar = Button(
            text="Guardar",
            background_normal="",
            background_color=COLOR_MORADO_BOTON,
            color=COLOR_BLANCO,
            bold=True
        )

        botones.add_widget(
            cancelar
        )

        botones.add_widget(
            guardar
        )

        contenido.add_widget(titulo)
        contenido.add_widget(cultivo)
        contenido.add_widget(fecha)
        contenido.add_widget(descripcion)
        contenido.add_widget(botones)

        popup = Popup(
            title="",
            content=contenido,
            size_hint=(0.90, None),
            height=dp(360),
            separator_color=COLOR_MORADO
        )

        cancelar.bind(
            on_release=popup.dismiss
        )

        guardar.bind(
            on_release=lambda instancia:
            self.guardar_evento(
                popup,
                actividad,
                fecha.text,
                descripcion.text
            )
        )

        popup.open()


    # =====================================================
    # GUARDAR EVENTO
    # =====================================================

    def guardar_evento(
        self,
        popup,
        tipo,
        fecha,
        descripcion
    ):

        tipo = tipo.strip()
        fecha = fecha.strip()
        descripcion = descripcion.strip()

        # -------------------------------------------------
        # VALIDAR FECHA
        # -------------------------------------------------

        if not fecha:

            self.mostrar_mensaje(
                "Debes ingresar una fecha."
            )

            return

        try:

            # Valida la fecha y la guarda siempre con ceros
            # (por ejemplo 2026-10-08)
            fecha = normalizar_fecha(fecha)

        except ValueError:

            self.mostrar_mensaje(
                "La fecha debe tener el formato "
                "YYYY-MM-DD."
            )

            return

        # -------------------------------------------------
        # GENERAR CÓDIGO
        # -------------------------------------------------

        ultimo_numero = 0

        for evento in self.gestor_calendario.eventos:

            if evento.codigo.startswith("EVT"):

                try:

                    numero = int(
                        evento.codigo[3:]
                    )

                    ultimo_numero = max(
                        ultimo_numero,
                        numero
                    )

                except ValueError:

                    pass

        nuevo_codigo = (
            f"EVT{ultimo_numero + 1:03d}"
        )

        # -------------------------------------------------
        # CREAR EVENTO
        # -------------------------------------------------

        nuevo_evento = EventoCalendario(
            codigo=nuevo_codigo,
            codigo_cultivo=(
                self.cultivo_seleccionado.codigo
            ),
            tipo=tipo,
            fecha=fecha,
            descripcion=descripcion
        )

        self.gestor_calendario.agregar_evento(
            nuevo_evento
        )

        popup.dismiss()

        self.actualizar_eventos()

        self.mostrar_mensaje(
            "Actividad agregada correctamente."
        )


    # =====================================================
    # AJUSTAR ALTURAS
    # =====================================================

    def actualizar_alturas(self):

        # -------------------------------------------------
        # ALTURA DE CULTIVOS
        # -------------------------------------------------

        cantidad_cultivos = len(
            self.lista_cultivos.children
        )

        if cantidad_cultivos > 0:

            self.lista_cultivos.height = (
                cantidad_cultivos * dp(88)
                + max(
                    0,
                    cantidad_cultivos - 1
                ) * dp(10)
            )

        # -------------------------------------------------
        # ALTURA DE EVENTOS
        # -------------------------------------------------

        cantidad_eventos = len(
            self.lista_eventos.children
        )

        if cantidad_eventos == 1:

            widget = self.lista_eventos.children[0]

            if widget.height == dp(55):

                self.lista_eventos.height = dp(55)

            else:

                self.lista_eventos.height = dp(78)

        elif cantidad_eventos > 1:

            self.lista_eventos.height = (
                cantidad_eventos * dp(78)
                + max(
                    0,
                    cantidad_eventos - 1
                ) * dp(10)
            )

        # -------------------------------------------------
        # ACTUALIZAR LAYOUT
        # -------------------------------------------------

        self.contenedor.do_layout()

        self.contenedor.height = (
            self.contenedor.minimum_height
        )


    # =====================================================
    # MENSAJE
    # =====================================================

    def mostrar_mensaje(self, mensaje):

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20)
        )

        texto = Label(
            text=mensaje,
            color=COLOR_TEXTO,
            font_size="14sp",
            halign="center",
            valign="middle"
        )

        texto.bind(
            size=lambda instancia, valor:
            setattr(
                instancia,
                "text_size",
                valor
            )
        )

        boton = Button(
            text="Aceptar",
            size_hint_y=None,
            height=dp(45),
            background_normal="",
            background_color=COLOR_MORADO_BOTON,
            color=COLOR_BLANCO
        )

        contenido.add_widget(
            texto
        )

        contenido.add_widget(
            boton
        )

        popup = Popup(
            title="",
            content=contenido,
            size_hint=(0.8, None),
            height=dp(190),
            separator_color=COLOR_MORADO
        )

        boton.bind(
            on_release=popup.dismiss
        )

        popup.open()