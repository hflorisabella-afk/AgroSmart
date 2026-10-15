from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

import os
import sys
from datetime import datetime, date
import calendar

sys.path.append(
    os.path.join(os.path.dirname(__file__), "..", "modelos")
)

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos

COLOR_FONDO = (0.10, 0.11, 0.14, 1)

COLOR_VERDE_PRINCIPAL = (0.30, 0.55, 0.38, 1)
COLOR_VERDE_OSCURO = (0.18, 0.34, 0.23, 1)
COLOR_VERDE_CLARO = (0.68, 0.88, 0.63, 1)

COLOR_TEXTO = (0.95, 0.97, 0.94, 1)
COLOR_TEXTO_SECUNDARIO = (0.70, 0.76, 0.71, 1)

COLOR_CAJA_TEXTO = (0.95, 0.97, 0.94, 1)
COLOR_TEXTO_CAJA = (0.10, 0.13, 0.11, 1)

COLOR_TARJETA = (0.12, 0.20, 0.15, 1)
COLOR_TARJETA_CLARA = (0.17, 0.27, 0.20, 1)

COLOR_ERROR = (0.95, 0.48, 0.45, 1)
COLOR_EXITO = (0.48, 0.82, 0.55, 1)
COLOR_INFO = (0.55, 0.76, 0.88, 1)

COLOR_ELIMINAR = (0.58, 0.29, 0.27, 1)
COLOR_CANCELAR = (0.35, 0.27, 0.29, 1)

Window.clearcolor = COLOR_FONDO
Window.size = (780, 850)

ALTURA_CAMPO = 48
ALTURA_TARJETA = 150

gestor = GestorCultivos()

class CampoRedondeado(BoxLayout):

    def __init__(self, texto="", hint_text="", **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            height=dp(ALTURA_CAMPO),
            padding=0,
            **kwargs
        )

        with self.canvas.before:

            Color(*COLOR_CAJA_TEXTO)

            self.rectangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        self.campo = TextInput(
            text=texto,
            hint_text=hint_text,
            multiline=False,
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=COLOR_TEXTO_CAJA,
            hint_text_color=(0.45, 0.48, 0.45, 1),
            cursor_color=COLOR_VERDE_PRINCIPAL,
            padding=[
                dp(15),
                dp(12),
                dp(15),
                dp(12)
            ]
        )

        self.add_widget(self.campo)

    def actualizar_fondo(self, instance, value):

        self.rectangulo.pos = self.pos
        self.rectangulo.size = self.size

    @property
    def text(self):

        return self.campo.text

    @text.setter
    def text(self, valor):

        self.campo.text = valor

    @property
    def focus(self):

        return self.campo.focus

    @focus.setter
    def focus(self, valor):

        self.campo.focus = valor

def caja_de_texto(texto="", hint_text=""):

    return CampoRedondeado(
        texto=texto,
        hint_text=hint_text
    )

def boton_estilizado(
    texto,
    color=COLOR_VERDE_PRINCIPAL,
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

    def actualizar_rectangulo(instance, value):

        boton.rectangulo.pos = boton.pos
        boton.rectangulo.size = boton.size

    boton.bind(
        pos=actualizar_rectangulo,
        size=actualizar_rectangulo
    )

    return boton

def etiqueta_seccion(texto):

    return Label(
        text=texto,
        color=COLOR_VERDE_CLARO,
        bold=True,
        font_size="17sp",
        size_hint_y=None,
        height=dp(35),
        halign="left",
        valign="middle"
    )

def fila_con_etiqueta(texto, hint=""):

    fila = BoxLayout(
        orientation="horizontal",
        spacing=dp(10),
        size_hint_y=None,
        height=dp(ALTURA_CAMPO)
    )

    etiqueta = Label(
        text=texto,
        color=COLOR_TEXTO,
        size_hint_x=0.32,
        halign="left",
        valign="middle"
    )

    etiqueta.bind(
        size=lambda instance, value:
        setattr(
            instance,
            "text_size",
            value
        )
    )

    caja = caja_de_texto(
        hint_text=hint
    )

    fila.add_widget(etiqueta)
    fila.add_widget(caja)

    return fila, caja

DEPARTAMENTOS_GUATEMALA = [
    "Alta Verapaz", "Baja Verapaz", "Chimaltenango", "Chiquimula",
    "El Progreso", "Escuintla", "Guatemala", "Huehuetenango",
    "Izabal", "Jalapa", "Jutiapa", "Petén", "Quetzaltenango",
    "Quiché", "Retalhuleu", "Sacatepéquez", "San Marcos",
    "Santa Rosa", "Sololá", "Suchitepéquez", "Totonicapán",
    "Zacapa"
]

class ControlLocalidad(BoxLayout):
    """Campo donde se puede escribir una localidad o elegir un departamento."""

    def __init__(self, texto="", **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(ALTURA_CAMPO),
            **kwargs
        )

        self.campo = TextInput(
            text=texto,
            hint_text="Escribe o selecciona un departamento",
            multiline=False,
            background_normal="",
            background_active="",
            background_color=COLOR_CAJA_TEXTO,
            foreground_color=COLOR_TEXTO_CAJA,
            hint_text_color=(0.45, 0.48, 0.45, 1),
            cursor_color=COLOR_VERDE_PRINCIPAL,
            padding=[dp(12), dp(12), dp(8), dp(12)]
        )
        self.add_widget(self.campo)

        self.boton_lista = boton_estilizado("Lista", COLOR_VERDE_OSCURO, ALTURA_CAMPO)
        self.boton_lista.size_hint_x = None
        self.boton_lista.width = dp(82)
        self.boton_lista.bind(on_release=self.abrir_lista)
        self.add_widget(self.boton_lista)

    @property
    def text(self):
        return self.campo.text

    @text.setter
    def text(self, valor):
        self.campo.text = str(valor or "")

    @property
    def focus(self):
        return self.campo.focus

    @focus.setter
    def focus(self, valor):
        self.campo.focus = valor

    def abrir_lista(self, *_):
        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12)
        )
        buscador = TextInput(
            hint_text="Buscar departamento...",
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            background_normal="",
            background_active="",
            background_color=COLOR_CAJA_TEXTO,
            foreground_color=COLOR_TEXTO_CAJA,
            cursor_color=COLOR_VERDE_PRINCIPAL,
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        contenido.add_widget(buscador)

        desplazamiento = ScrollView()
        opciones = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )
        opciones.bind(minimum_height=opciones.setter("height"))
        desplazamiento.add_widget(opciones)
        contenido.add_widget(desplazamiento)

        popup = Popup(
            title="Seleccionar departamento",
            content=contenido,
            size_hint=(0.86, 0.82),
            auto_dismiss=True
        )

        def actualizar_opciones(texto=""):
            opciones.clear_widgets()
            coincidencias = [
                d for d in DEPARTAMENTOS_GUATEMALA
                if texto.strip().casefold() in d.casefold()
            ]
            if not coincidencias:
                opciones.add_widget(Label(
                    text="No se encontraron coincidencias.",
                    color=COLOR_TEXTO,
                    size_hint_y=None,
                    height=dp(42)
                ))
                return

            for departamento in coincidencias:
                boton = boton_estilizado(
                    departamento, COLOR_VERDE_OSCURO, 42
                )
                boton.bind(
                    on_release=lambda instancia, valor=departamento:
                    seleccionar(valor)
                )
                opciones.add_widget(boton)

        def seleccionar(valor):
            self.text = valor
            popup.dismiss()

        buscador.bind(text=lambda instancia, valor: actualizar_opciones(valor))
        actualizar_opciones()
        popup.open()

MESES_ESPANOL = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]

class ControlFecha(BoxLayout):
    """Fecha que acepta escritura manual YYYY-MM-DD o selección en calendario."""

    def __init__(self, texto="", **kwargs):
        super().__init__(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(ALTURA_CAMPO),
            **kwargs
        )

        self.campo = TextInput(
            text=texto,
            hint_text="YYYY-MM-DD",
            multiline=False,
            background_normal="",
            background_active="",
            background_color=COLOR_CAJA_TEXTO,
            foreground_color=COLOR_TEXTO_CAJA,
            hint_text_color=(0.45, 0.48, 0.45, 1),
            cursor_color=COLOR_VERDE_PRINCIPAL,
            padding=[dp(12), dp(12), dp(8), dp(12)]
        )
        self.add_widget(self.campo)

        self.boton_calendario = boton_estilizado(
            "Calendario", COLOR_VERDE_OSCURO, ALTURA_CAMPO
        )
        self.boton_calendario.size_hint_x = None
        self.boton_calendario.width = dp(112)
        self.boton_calendario.bind(on_release=self.abrir_calendario)
        self.add_widget(self.boton_calendario)

    @property
    def text(self):
        return self.campo.text

    @text.setter
    def text(self, valor):
        self.campo.text = str(valor or "")

    @property
    def focus(self):
        return self.campo.focus

    @focus.setter
    def focus(self, valor):
        self.campo.focus = valor

    def abrir_calendario(self, *_):
        try:
            inicial = datetime.strptime(self.text.strip(), "%Y-%m-%d").date()
        except ValueError:
            inicial = date.today()

        estado = {"anio": inicial.year, "mes": inicial.month}

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(12)
        )

        encabezado = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(42)
        )
        boton_anterior = boton_estilizado("<", COLOR_VERDE_OSCURO, 42)
        boton_siguiente = boton_estilizado(">", COLOR_VERDE_OSCURO, 42)
        titulo_mes = Label(
            text="",
            color=COLOR_TEXTO,
            bold=True,
            font_size="17sp"
        )
        encabezado.add_widget(boton_anterior)
        encabezado.add_widget(titulo_mes)
        encabezado.add_widget(boton_siguiente)
        contenido.add_widget(encabezado)

        calendario_grid = GridLayout(
            cols=7,
            spacing=dp(3),
            size_hint_y=None
        )
        calendario_grid.bind(minimum_height=calendario_grid.setter("height"))
        contenido.add_widget(calendario_grid)

        popup = Popup(
            title="Seleccionar fecha de siembra",
            content=contenido,
            size_hint=(0.88, 0.58),
            auto_dismiss=True
        )

        def seleccionar_dia(dia):
            self.text = f"{estado['anio']:04d}-{estado['mes']:02d}-{dia:02d}"
            popup.dismiss()

        def dibujar_calendario():
            calendario_grid.clear_widgets()
            titulo_mes.text = (
                f"{MESES_ESPANOL[estado['mes'] - 1].capitalize()} {estado['anio']}"
            )
            for nombre_dia in ("L", "M", "X", "J", "V", "S", "D"):
                calendario_grid.add_widget(Label(
                    text=nombre_dia,
                    color=COLOR_VERDE_CLARO,
                    bold=True,
                    size_hint_y=None,
                    height=dp(30)
                ))

            semanas = calendar.monthcalendar(estado["anio"], estado["mes"])
            for semana in semanas:
                for dia in semana:
                    if dia == 0:
                        calendario_grid.add_widget(Label(
                            text="",
                            size_hint_y=None,
                            height=dp(38)
                        ))
                    else:
                        boton = boton_estilizado(
                            str(dia), COLOR_VERDE_PRINCIPAL, 38
                        )
                        boton.bind(
                            on_release=lambda instancia, valor=dia:
                            seleccionar_dia(valor)
                        )
                        calendario_grid.add_widget(boton)

        def cambiar_mes(cantidad):
            nuevo_mes = estado["mes"] + cantidad
            if nuevo_mes < 1:
                estado["mes"] = 12
                estado["anio"] -= 1
            elif nuevo_mes > 12:
                estado["mes"] = 1
                estado["anio"] += 1
            else:
                estado["mes"] = nuevo_mes
            dibujar_calendario()

        boton_anterior.bind(on_release=lambda *_: cambiar_mes(-1))
        boton_siguiente.bind(on_release=lambda *_: cambiar_mes(1))
        dibujar_calendario()
        popup.open()

def fila_con_control(texto, control):
    fila = BoxLayout(
        orientation="horizontal",
        spacing=dp(10),
        size_hint_y=None,
        height=dp(ALTURA_CAMPO)
    )

    etiqueta = Label(
        text=texto,
        color=COLOR_TEXTO,
        size_hint_x=0.32,
        halign="left",
        valign="middle"
    )
    etiqueta.bind(
        size=lambda instancia, valor:
        setattr(instancia, "text_size", valor)
    )

    control.size_hint_x = 0.68
    fila.add_widget(etiqueta)
    fila.add_widget(control)
    return fila, control

class PantallaCultivos(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.do_scroll_x = False

        self.en_edicion = None

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[
                dp(25),
                dp(25),
                dp(25),
                dp(35)
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

        titulo = Label(
            text="CULTIVOS",
            color=COLOR_VERDE_CLARO,
            font_size="30sp",
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )

        subtitulo = Label(
            text="Registra y administra tus cultivos",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="15sp",
            size_hint_y=None,
            height=dp(35)
        )

        self.contenedor.add_widget(titulo)
        self.contenedor.add_widget(subtitulo)

        self.contenedor.add_widget(
            etiqueta_seccion(
                "REGISTRAR CULTIVO"
            )
        )

        fila, self.campo_nombre = fila_con_etiqueta(
            "Nombre:",
            "Ej. Mi parcela"
        )

        self.contenedor.add_widget(fila)

        fila, self.campo_tipo = fila_con_etiqueta(
            "Tipo:",
            "Ej. Maíz"
        )

        self.contenedor.add_widget(fila)

        fila, self.campo_tierra = fila_con_etiqueta(
            "Tierra:",
            "Ej. Arcillosa"
        )

        self.contenedor.add_widget(fila)

        self.campo_localidad = ControlLocalidad()
        fila, self.campo_localidad = fila_con_control(
            "Localidad:", self.campo_localidad
        )

        self.contenedor.add_widget(fila)

        fila, self.campo_parcela = fila_con_etiqueta(
            "Parcela:",
            "Ej. 001"
        )

        self.contenedor.add_widget(fila)

        fila, self.campo_tamano = fila_con_etiqueta(
            "Tamaño (ha):",
            "Ej. 2.5"
        )

        self.contenedor.add_widget(fila)

        self.campo_fecha = ControlFecha()
        fila, self.campo_fecha = fila_con_control(
            "Siembra:", self.campo_fecha
        )

        self.contenedor.add_widget(fila)

        self.mensaje = Label(
            text="",
            color=COLOR_INFO,
            font_size="14sp",
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle"
        )

        self.mensaje.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(
            self.mensaje
        )

        fila_botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(48)
        )

        self.boton_registrar = boton_estilizado(
            "Registrar cultivo"
        )

        self.boton_registrar.bind(
            on_release=self.registrar_cultivo
        )

        boton_limpiar = boton_estilizado(
            "Limpiar",
            COLOR_CANCELAR
        )

        boton_limpiar.bind(
            on_release=lambda instance:
            self._limpiar_formulario()
        )

        fila_botones.add_widget(
            self.boton_registrar
        )

        fila_botones.add_widget(
            boton_limpiar
        )

        self.contenedor.add_widget(
            fila_botones
        )

        self.contenedor.add_widget(
            etiqueta_seccion(
                "BUSCAR CULTIVO"
            )
        )

        self.campo_busqueda = caja_de_texto(
            hint_text=(
                "Nombre, tipo, localidad o parcela"
            )
        )

        self.contenedor.add_widget(
            self.campo_busqueda
        )

        boton_buscar = boton_estilizado(
            "Buscar cultivo",
            COLOR_VERDE_OSCURO
        )

        boton_buscar.bind(
            on_release=self.buscar_cultivo
        )

        self.contenedor.add_widget(
            boton_buscar
        )

        self.resultado_busqueda = Label(
            text="",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="14sp",
            size_hint_y=None,
            height=dp(50),
            halign="left",
            valign="middle"
        )

        self.resultado_busqueda.bind(
            size=lambda instance, value:
            setattr(
                instance,
                "text_size",
                value
            )
        )

        self.contenedor.add_widget(
            self.resultado_busqueda
        )

        self.contenedor.add_widget(
            etiqueta_seccion(
                "ORDENAR"
            )
        )

        boton_ordenar = boton_estilizado(
            "Ordenar por fecha de siembra",
            COLOR_VERDE_OSCURO
        )

        boton_ordenar.bind(
            on_release=self.ordenar_cultivos
        )

        self.contenedor.add_widget(
            boton_ordenar
        )

        self.contenedor.add_widget(
            etiqueta_seccion(
                "ELIMINAR CULTIVO"
            )
        )

        self.campo_codigo_eliminar = caja_de_texto(
            hint_text="Ej. CULT001"
        )

        self.contenedor.add_widget(
            self.campo_codigo_eliminar
        )

        boton_eliminar = boton_estilizado(
            "Eliminar cultivo",
            COLOR_ELIMINAR
        )

        boton_eliminar.bind(
            on_release=self.eliminar_cultivo
        )

        self.contenedor.add_widget(
            boton_eliminar
        )

        self.contenedor.add_widget(
            etiqueta_seccion(
                "TUS CULTIVOS"
            )
        )

        self.lista_cultivos = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.lista_cultivos.bind(
            minimum_height=self.lista_cultivos.setter(
                "height"
            )
        )

        self.contenedor.add_widget(
            self.lista_cultivos
        )

        self.actualizar_lista()

    def registrar_cultivo(self, instance):

        nombre = self.campo_nombre.text.strip()
        tipo = self.campo_tipo.text.strip()
        tierra = self.campo_tierra.text.strip()
        localidad = self.campo_localidad.text.strip()
        parcela = self.campo_parcela.text.strip()
        tamano = self.campo_tamano.text.strip()
        fecha = self.campo_fecha.text.strip()

        if not all([
            nombre,
            tipo,
            tierra,
            localidad,
            parcela,
            tamano,
            fecha
        ]):

            self.mensaje.text = (
                "Completa todos los campos."
            )

            self.mensaje.color = COLOR_ERROR

            return

        try:

            tamano_numero = float(tamano)

            if tamano_numero <= 0:
                raise ValueError

        except ValueError:

            self.mensaje.text = (
                "El tamaño debe ser un número "
                "mayor que 0."
            )

            self.mensaje.color = COLOR_ERROR

            return

        try:

            datetime.strptime(
                fecha,
                "%Y-%m-%d"
            )

        except ValueError:

            self.mensaje.text = (
                "La fecha debe tener el formato "
                "YYYY-MM-DD."
            )

            self.mensaje.color = COLOR_ERROR

            return

        if self.en_edicion:

            cultivo = gestor.buscar_por_codigo_hash(
                self.en_edicion
            )

            if cultivo is None:

                self.mensaje.text = (
                    "No se encontró el cultivo."
                )

                self.mensaje.color = COLOR_ERROR

                return

            cultivo.nombre = nombre
            cultivo.tipo = tipo
            cultivo.tipo_tierra = tierra
            cultivo.localidad = localidad
            cultivo.numero_parcela = parcela
            cultivo.tamano_parcela = tamano_numero
            cultivo.fecha_siembra = fecha

            gestor.guardar_datos()

            self.mensaje.text = (
                "Cultivo actualizado correctamente."
            )

            self.mensaje.color = COLOR_EXITO

            self._salir_de_modo_edicion()

            self.actualizar_lista()

            return

        codigo = gestor.generar_codigo()

        nuevo_cultivo = Cultivo(
            codigo,
            nombre,
            tipo,
            tierra,
            localidad,
            parcela,
            tamano_numero,
            fecha
        )

        gestor.agregar_cultivo(
            nuevo_cultivo
        )

        self.mensaje.text = (
            "Cultivo registrado correctamente. "
            f"Código: {codigo}"
        )

        self.mensaje.color = COLOR_EXITO

        self._limpiar_formulario()

        self.actualizar_lista()

    def _limpiar_formulario(self):

        self.campo_nombre.text = ""
        self.campo_tipo.text = ""
        self.campo_tierra.text = ""
        self.campo_localidad.text = ""
        self.campo_parcela.text = ""
        self.campo_tamano.text = ""
        self.campo_fecha.text = ""

        self.en_edicion = None

        if hasattr(
            self,
            "boton_registrar"
        ):

            self.boton_registrar.text = (
                "Registrar cultivo"
            )

    def _entrar_a_modo_edicion(self, codigo):

        cultivo = gestor.buscar_por_codigo_hash(
            codigo
        )

        if cultivo is None:

            self.mensaje.text = (
                "No se encontró el cultivo."
            )

            self.mensaje.color = COLOR_ERROR

            return

        self.en_edicion = codigo

        self.campo_nombre.text = cultivo.nombre
        self.campo_tipo.text = cultivo.tipo
        self.campo_tierra.text = cultivo.tipo_tierra
        self.campo_localidad.text = cultivo.localidad

        self.campo_parcela.text = str(
            cultivo.numero_parcela
        )

        self.campo_tamano.text = str(
            cultivo.tamano_parcela
        )

        self.campo_fecha.text = (
            cultivo.fecha_siembra
        )

        self.boton_registrar.text = (
            "Guardar cambios"
        )

        self.mensaje.text = (
            f"Editando cultivo {codigo}"
        )

        self.mensaje.color = COLOR_INFO

    def _salir_de_modo_edicion(self):

        self.en_edicion = None

        self.boton_registrar.text = (
            "Registrar cultivo"
        )

    def cancelar_edicion(self):

        self._limpiar_formulario()

        self.mensaje.text = (
            "Edición cancelada."
        )

        self.mensaje.color = COLOR_INFO

    def buscar_cultivo(self, instance):

        texto = (
            self.campo_busqueda.text.strip()
        )

        if not texto:

            self.resultado_busqueda.text = (
                "Escribe algo para buscar."
            )

            return

        resultados = gestor.buscar_coincidencias(
            texto
        )

        if not resultados:

            self.resultado_busqueda.text = (
                "No se encontraron cultivos."
            )

            return

        texto_resultado = "Resultados:\n"

        for cultivo in resultados:

            texto_resultado += (
                f"{cultivo.codigo} - "
                f"{cultivo.nombre} - "
                f"{cultivo.tipo}\n"
            )

        self.resultado_busqueda.text = (
            texto_resultado
        )

        self.mostrar_seleccionado(
            resultados[0]
        )

    def mostrar_seleccionado(self, cultivo):

        self.campo_codigo_eliminar.text = (
            cultivo.codigo
        )

    def ordenar_cultivos(self, instance):

        gestor.ordenar_por_fecha_siembra()

        self.mensaje.text = (
            "Cultivos ordenados por fecha "
            "de siembra."
        )

        self.mensaje.color = COLOR_INFO

        self.actualizar_lista()

    def eliminar_cultivo(self, instance):

        codigo = (
            self.campo_codigo_eliminar.text.strip()
        )

        if not codigo:

            self.mensaje.text = (
                "Escribe el código del cultivo."
            )

            self.mensaje.color = COLOR_ERROR

            return

        codigo_normalizado = (
            self._normalizar_codigo(codigo)
        )

        cultivo = gestor.buscar_por_codigo_hash(
            codigo_normalizado
        )

        if cultivo is None:

            self.mensaje.text = (
                f"No existe el cultivo "
                f"{codigo_normalizado}."
            )

            self.mensaje.color = COLOR_ERROR

            return

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(15)
        )

        mensaje = Label(
            text=(
                "¿Seguro que deseas eliminar?\n\n"
                f"{cultivo.codigo} - "
                f"{cultivo.nombre}"
            ),
            color=COLOR_TEXTO,
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

        botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(45)
        )

        boton_si = boton_estilizado(
            "Eliminar",
            COLOR_ELIMINAR,
            45
        )

        boton_no = boton_estilizado(
            "Cancelar",
            COLOR_CANCELAR,
            45
        )

        botones.add_widget(
            boton_si
        )

        botones.add_widget(
            boton_no
        )

        contenido.add_widget(
            mensaje
        )

        contenido.add_widget(
            botones
        )

        popup = Popup(
            title="Confirmar eliminación",
            content=contenido,
            size_hint=(0.8, 0.35)
        )

        def confirmar_eliminacion(instance):

            gestor.eliminar_cultivo(
                codigo_normalizado
            )

            popup.dismiss()

            self._eliminacion_exitosa()

        boton_si.bind(
            on_release=confirmar_eliminacion
        )

        boton_no.bind(
            on_release=popup.dismiss
        )

        popup.open()

    def _eliminacion_exitosa(self):

        self.campo_codigo_eliminar.text = ""

        self.mensaje.text = (
            "Cultivo eliminado correctamente."
        )

        self.mensaje.color = COLOR_EXITO

        self.actualizar_lista()

    def _normalizar_codigo(self, codigo):

        codigo = codigo.strip().upper()

        if codigo.startswith("CULT"):

            numero = codigo.replace(
                "CULT",
                ""
            )

        else:

            numero = codigo

        try:

            numero = int(numero)

            return f"CULT{numero:03d}"

        except ValueError:

            return codigo

    def actualizar_lista(self):

        self.lista_cultivos.clear_widgets()

        cultivos = gestor.lista_cultivos

        if not cultivos:

            mensaje = Label(
                text=(
                    "No hay cultivos registrados "
                    "todavía."
                ),
                color=COLOR_TEXTO_SECUNDARIO,
                font_size="14sp",
                size_hint_y=None,
                height=dp(60)
            )

            self.lista_cultivos.add_widget(
                mensaje
            )

            return

        for cultivo in cultivos:

            tarjeta = BoxLayout(
                orientation="vertical",
                spacing=dp(4),
                padding=[
                    dp(15),
                    dp(10),
                    dp(15),
                    dp(10)
                ],
                size_hint_y=None,
                height=dp(ALTURA_TARJETA)
            )

            with tarjeta.canvas.before:

                Color(*COLOR_TARJETA)

                tarjeta.rectangulo = RoundedRectangle(
                    pos=tarjeta.pos,
                    size=tarjeta.size,
                    radius=[dp(14)]
                )

            def actualizar_tarjeta(
                instance,
                value,
                tarjeta=tarjeta
            ):

                tarjeta.rectangulo.pos = (
                    tarjeta.pos
                )

                tarjeta.rectangulo.size = (
                    tarjeta.size
                )

            tarjeta.bind(
                pos=actualizar_tarjeta,
                size=actualizar_tarjeta
            )

            encabezado = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(28)
            )

            nombre = Label(
                text=cultivo.nombre,
                color=COLOR_VERDE_CLARO,
                bold=True,
                font_size="17sp",
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

            codigo = Label(
                text=(
                    f"CÓDIGO: {cultivo.codigo}"
                ),
                color=COLOR_TEXTO,
                bold=True,
                font_size="13sp",
                size_hint_x=0.40,
                halign="right",
                valign="middle"
            )

            codigo.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            encabezado.add_widget(
                nombre
            )

            encabezado.add_widget(
                codigo
            )

            tarjeta.add_widget(
                encabezado
            )

            info1 = Label(
                text=(
                    f"Tipo: {cultivo.tipo}    "
                    f"Tierra: {cultivo.tipo_tierra}"
                ),
                color=COLOR_TEXTO,
                font_size="13sp",
                halign="left",
                valign="middle"
            )

            info1.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            info2 = Label(
                text=(
                    f"Localidad: "
                    f"{cultivo.localidad}    "
                    f"Parcela: "
                    f"{cultivo.numero_parcela}    "
                    f"Tamaño: "
                    f"{cultivo.tamano_parcela} ha"
                ),
                color=COLOR_TEXTO_SECUNDARIO,
                font_size="13sp",
                halign="left",
                valign="middle"
            )

            info2.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            info3 = Label(
                text=(
                    f"Siembra: "
                    f"{cultivo.fecha_siembra}    "
                    f"Estado: "
                    f"{cultivo.estado}"
                ),
                color=COLOR_TEXTO_SECUNDARIO,
                font_size="13sp",
                halign="left",
                valign="middle"
            )

            info3.bind(
                size=lambda instance, value:
                setattr(
                    instance,
                    "text_size",
                    value
                )
            )

            tarjeta.add_widget(
                info1
            )

            tarjeta.add_widget(
                info2
            )

            tarjeta.add_widget(
                info3
            )

            boton_editar = boton_estilizado(
                "Editar cultivo",
                COLOR_VERDE_OSCURO,
                34
            )

            boton_editar.bind(
                on_release=lambda instance,
                codigo=cultivo.codigo:
                self._entrar_a_modo_edicion(
                    codigo
                )
            )

            tarjeta.add_widget(
                boton_editar
            )

            self.lista_cultivos.add_widget(
                tarjeta
            )

class AgroSmartApp(App):

    def build(self):

        return PantallaCultivos()

if __name__ == "__main__":

    AgroSmartApp().run()
