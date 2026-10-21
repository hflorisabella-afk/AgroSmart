import os
import sys
from datetime import datetime

from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import escape_markup

sys.path.append(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "modelos")
)

from gestor_cultivos import GestorCultivos
from planificador import Planificador


# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = (0.17, 0.11, 0.07, 1)

COLOR_NARANJA_PRINCIPAL = (0.82, 0.47, 0.20, 1)
COLOR_NARANJA_OSCURO = (0.48, 0.27, 0.12, 1)
COLOR_NARANJA_CLARO = (0.98, 0.78, 0.55, 1)

COLOR_TEXTO = (0.97, 0.94, 0.90, 1)
COLOR_TEXTO_SECUNDARIO = (0.78, 0.70, 0.62, 1)

COLOR_CAJA = (0.97, 0.94, 0.90, 1)
COLOR_TEXTO_CAJA = (0.15, 0.10, 0.06, 1)

COLOR_TARJETA = (0.26, 0.17, 0.11, 1)

COLOR_ERROR = (0.95, 0.48, 0.45, 1)
COLOR_EXITO = (0.55, 0.85, 0.60, 1)
COLOR_INFO = (0.98, 0.78, 0.55, 1)


def hex_color(color):
    # Convierte (0.5, 0.2, 0.1, 1) en "803319" para usarlo en textos con color
    return "%02x%02x%02x" % tuple(int(x * 255) for x in color[:3])


# ============================================================
# WIDGETS AUXILIARES
# ============================================================

def boton_estilizado(texto, color=COLOR_NARANJA_PRINCIPAL, altura=48):

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

    def actualizar(instancia, valor):

        boton.rectangulo.pos = boton.pos
        boton.rectangulo.size = boton.size

    boton.bind(pos=actualizar, size=actualizar)

    return boton


def caja_de_texto(hint, filtro=None):

    return TextInput(
        hint_text=hint,
        multiline=False,
        input_filter=filtro,
        size_hint_y=None,
        height=dp(46),
        background_normal="",
        background_active="",
        background_color=COLOR_CAJA,
        foreground_color=COLOR_TEXTO_CAJA,
        hint_text_color=(0.45, 0.40, 0.36, 1),
        cursor_color=COLOR_NARANJA_PRINCIPAL,
        padding=[dp(14), dp(12), dp(14), dp(12)]
    )


def selector(texto_inicial):

    return Spinner(
        text=texto_inicial,
        values=[],
        size_hint_y=None,
        height=dp(46),
        background_normal="",
        background_color=COLOR_NARANJA_OSCURO,
        color=COLOR_TEXTO,
        bold=True
    )


def etiqueta_seccion(texto):

    etiqueta = Label(
        text=texto,
        color=COLOR_NARANJA_CLARO,
        bold=True,
        font_size="17sp",
        size_hint_y=None,
        height=dp(38),
        halign="left",
        valign="middle"
    )

    etiqueta.bind(
        size=lambda instancia, valor:
        setattr(instancia, "text_size", valor)
    )

    return etiqueta


class TextoAyuda(Label):
    """Texto pequeño que se acomoda solo en varias líneas."""

    def __init__(self, texto, **kwargs):

        super().__init__(
            text=texto,
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="13sp",
            size_hint_y=None,
            halign="left",
            valign="top",
            **kwargs
        )

        self.bind(
            width=lambda instancia, valor:
            setattr(instancia, "text_size", (valor, None))
        )

        self.bind(
            texture_size=lambda instancia, tamano:
            setattr(instancia, "height", tamano[1] + dp(6))
        )


class CuadroTexto(BoxLayout):
    """Tarjeta que crece sola según el texto que tenga adentro."""

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(12),
            **kwargs
        )

        self.height = dp(60)

        with self.canvas.before:

            Color(*COLOR_TARJETA)

            self.fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(12)]
            )

        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

        self.etiqueta = Label(
            text="",
            color=COLOR_TEXTO,
            font_size="14sp",
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.etiqueta.bind(
            width=lambda instancia, valor:
            setattr(instancia, "text_size", (valor, None))
        )

        self.etiqueta.bind(texture_size=self._ajustar_altura)

        self.add_widget(self.etiqueta)

    def _actualizar_fondo(self, *_):

        self.fondo.pos = self.pos
        self.fondo.size = self.size

    def _ajustar_altura(self, instancia, tamano):

        instancia.height = tamano[1]
        self.height = max(dp(60), tamano[1] + dp(24))

    def poner(self, texto):

        self.etiqueta.text = texto


class TarjetaCultivo(BoxLayout):
    """Una tarjeta por cultivo: datos, recomendación de agua y un botón."""

    def __init__(self, texto, texto_boton, al_presionar, boton_activo=True, **kwargs):

        super().__init__(
            orientation="vertical",
            size_hint_y=None,
            padding=dp(14),
            spacing=dp(8),
            **kwargs
        )

        self.height = dp(190)

        with self.canvas.before:

            Color(*COLOR_TARJETA)

            self.fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(14)]
            )

        self.bind(pos=self._actualizar_fondo, size=self._actualizar_fondo)

        self.etiqueta = Label(
            text=texto,
            markup=True,
            color=COLOR_TEXTO,
            font_size="14sp",
            size_hint_y=None,
            halign="left",
            valign="top"
        )

        self.etiqueta.bind(
            width=lambda instancia, valor:
            setattr(instancia, "text_size", (valor, None))
        )

        self.etiqueta.bind(texture_size=self._ajustar_altura)

        self.add_widget(self.etiqueta)

        if boton_activo:

            self.boton = boton_estilizado(texto_boton, COLOR_NARANJA_PRINCIPAL, 42)

            self.boton.bind(on_release=lambda *_: al_presionar())

        else:

            self.boton = boton_estilizado(texto_boton, COLOR_NARANJA_OSCURO, 42)

            self.boton.disabled = True

            self.boton.opacity = 0.65

        self.add_widget(self.boton)

    def _actualizar_fondo(self, *_):

        self.fondo.pos = self.pos
        self.fondo.size = self.size

    def _ajustar_altura(self, instancia, tamano):

        instancia.height = tamano[1]
        # texto + botón (42) + espacio entre ambos (8) + márgenes de arriba y abajo (28)
        self.height = tamano[1] + dp(42) + dp(8) + dp(28)


# ============================================================
# PANTALLA OPTIMIZAR
# ============================================================

class PantallaOptimizacion(ScrollView):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.do_scroll_x = False

        self.gestor = GestorCultivos()
        self.planificador = Planificador()

        self.mapa_nodos = {}      # texto del menú -> código (incluye el tanque)
        self.mapa_cultivos = {}   # texto del menú -> código (solo cultivos)

        self.contenedor = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=[dp(22), dp(22), dp(22), dp(35)],
            size_hint_y=None
        )

        self.contenedor.bind(
            minimum_height=self.contenedor.setter("height")
        )

        self.add_widget(self.contenedor)

        self._construir()
        self.actualizar_lista()

    # ========================================================
    # CONSTRUIR LA PANTALLA
    # ========================================================

    def _construir(self):

        c = self.contenedor

        titulo = Label(
            text="OPTIMIZAR",
            color=COLOR_NARANJA_CLARO,
            font_size="30sp",
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )

        subtitulo = Label(
            text="Te ayudamos a usar mejor el agua de tus cultivos",
            color=COLOR_TEXTO_SECUNDARIO,
            font_size="14sp",
            size_hint_y=None,
            height=dp(30)
        )

        c.add_widget(titulo)
        c.add_widget(subtitulo)

        # Guía rápida
        guia = CuadroTexto()
        guia.poner(
            "¿Cómo usar esta pantalla?\n"
            "1. Mira cuánta agua necesita cada uno de tus cultivos.\n"
            "2. Agrega a 'Pendientes' los que vas a regar.\n"
            "3. Si no te alcanza el agua, pide que te ayudemos a repartirla."
        )
        c.add_widget(guia)

        # Mensaje general (avisos y errores)
        self.mensaje = Label(
            text="",
            color=COLOR_INFO,
            font_size="14sp",
            size_hint_y=None,
            height=dp(40),
            halign="center",
            valign="middle"
        )

        self.mensaje.bind(
            size=lambda instancia, valor:
            setattr(instancia, "text_size", valor)
        )

        c.add_widget(self.mensaje)

        # ----------------------------------------------------
        # 1. TUS CULTIVOS Y EL AGUA QUE NECESITAN
        # ----------------------------------------------------

        c.add_widget(etiqueta_seccion("1. TUS CULTIVOS Y SU AGUA"))

        c.add_widget(TextoAyuda(
            "Son cantidades aproximadas por riego. Dependen del tipo de "
            "cultivo, del tamaño de la parcela y de la tierra."
        ))

        self.lista_tarjetas = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None
        )

        self.lista_tarjetas.bind(
            minimum_height=self.lista_tarjetas.setter("height")
        )

        c.add_widget(self.lista_tarjetas)

        # ----------------------------------------------------
        # 2. PENDIENTES POR REGAR
        # ----------------------------------------------------

        c.add_widget(etiqueta_seccion("2. PENDIENTES POR REGAR"))

        c.add_widget(TextoAyuda(
            "Se riegan en el orden en que los agregaste. "
            "El primero de la lista es el siguiente."
        ))

        self.cuadro_cola = CuadroTexto()
        c.add_widget(self.cuadro_cola)

        boton_siguiente = boton_estilizado("Ya regué el siguiente")
        boton_siguiente.bind(on_release=self.atender_siguiente)
        c.add_widget(boton_siguiente)

        c.add_widget(etiqueta_seccion("RIEGOS YA HECHOS"))

        self.cuadro_historial = CuadroTexto()
        c.add_widget(self.cuadro_historial)

        # ----------------------------------------------------
        # 3. REPARTIR EL AGUA
        # ----------------------------------------------------

        c.add_widget(etiqueta_seccion("3. ¿NO TE ALCANZA EL AGUA? REPÁRTELA"))

        self.texto_total = TextoAyuda("")
        c.add_widget(self.texto_total)

        self.campo_agua = caja_de_texto(
            "¿Cuántos litros de agua tienes? (ej. 500000)",
            "float"
        )
        c.add_widget(self.campo_agua)

        boton_repartir = boton_estilizado("Repartir mi agua")
        boton_repartir.bind(on_release=self.repartir_agua)
        c.add_widget(boton_repartir)

        self.cuadro_reparto = CuadroTexto()
        self.cuadro_reparto.poner(
            "Aquí te diremos cuánta agua darle a cada cultivo."
        )
        c.add_widget(self.cuadro_reparto)

        # ----------------------------------------------------
        # 4. CAMINO DEL AGUA
        # ----------------------------------------------------

        c.add_widget(etiqueta_seccion("4. CAMINO DEL AGUA"))

        c.add_widget(TextoAyuda(
            "Anota por dónde pasan tus tuberías o canales. Después te "
            "mostramos el camino más corto desde el tanque hasta cada cultivo."
        ))

        c.add_widget(TextoAyuda(
            "Paso A: conecta dos lugares con una tubería o canal."
        ))

        self.sp_desde = selector("Elige el punto de salida")
        c.add_widget(self.sp_desde)

        self.sp_hasta = selector("Elige el punto de llegada")
        c.add_widget(self.sp_hasta)

        self.campo_metros = caja_de_texto(
            "Distancia en metros (ej. 150)",
            "float"
        )
        c.add_widget(self.campo_metros)

        boton_conexion = boton_estilizado("Guardar conexión")
        boton_conexion.bind(on_release=self.agregar_canal)
        c.add_widget(boton_conexion)

        self.cuadro_canales = CuadroTexto()
        c.add_widget(self.cuadro_canales)

        boton_borrar = boton_estilizado(
            "Borrar todas las conexiones",
            COLOR_NARANJA_OSCURO,
            42
        )
        boton_borrar.bind(on_release=self.borrar_canales)
        c.add_widget(boton_borrar)

        c.add_widget(TextoAyuda(
            "Paso B: elige un cultivo y mira el camino más corto desde el tanque."
        ))

        self.sp_destino = selector("Elige un cultivo")
        c.add_widget(self.sp_destino)

        boton_ruta = boton_estilizado("Ver camino más corto")
        boton_ruta.bind(on_release=self.calcular_ruta)
        c.add_widget(boton_ruta)

        self.cuadro_ruta = CuadroTexto()
        self.cuadro_ruta.poner("Aquí aparecerá el camino más corto.")
        c.add_widget(self.cuadro_ruta)

    # ========================================================
    # UTILIDADES
    # ========================================================

    def _decir(self, texto, color=COLOR_INFO):

        self.mensaje.text = texto
        self.mensaje.color = color

    def _nombre(self, codigo):

        cultivo = self.gestor.buscar_por_codigo_hash(codigo)

        if cultivo is None:
            return f"{codigo} (cultivo eliminado)"

        return cultivo.nombre

    def _nombre_nodo(self, codigo):

        if codigo == "TANQUE":
            return "Tanque de agua"

        return self._nombre(codigo)

    # ========================================================
    # ACTUALIZAR (se llama cada vez que se entra a la pantalla)
    # ========================================================

    def actualizar_lista(self):

        self.gestor = GestorCultivos()

        self._refrescar_tarjetas()
        self._refrescar_cola()
        self._refrescar_historial()
        self._refrescar_canales()
        self._refrescar_selectores()
        self._refrescar_total()

    def _refrescar_tarjetas(self):

        self.lista_tarjetas.clear_widgets()

        cultivos = self.gestor.lista_cultivos

        if not cultivos:

            self.lista_tarjetas.add_widget(TextoAyuda(
                "Todavía no tienes cultivos. Regístralos primero "
                "en la pantalla Cultivos."
            ))

            return

        colores_estado = {
            "urgente": COLOR_ERROR,
            "bien": COLOR_EXITO,
            "pendiente": COLOR_INFO,
            "info": COLOR_TEXTO_SECUNDARIO,
        }

        for cultivo in cultivos:

            rec = self.planificador.recomendar(cultivo)

            texto_estado, clave = self.planificador.estado_riego(cultivo, rec)

            try:
                tamano = f"{float(cultivo.tamano_parcela):g}"
            except (TypeError, ValueError):
                tamano = str(cultivo.tamano_parcela)

            texto = (
                f"[b][size=17sp][color={hex_color(COLOR_NARANJA_CLARO)}]"
                f"{escape_markup(cultivo.nombre)}"
                f"[/color][/size][/b]   ({escape_markup(cultivo.codigo)})\n"
                f"{escape_markup(cultivo.tipo)}  ·  {tamano} hectáreas  ·  "
                f"tierra {escape_markup(cultivo.tipo_tierra)}\n"
                f"Etapa: {rec['etapa_texto']}\n"
                f"[b]Recomendación:[/b] regar unos "
                f"[b]{rec['litros']:,.0f} litros[/b] cada "
                f"[b]{rec['dias']} días[/b]\n"
                f"[color={hex_color(colores_estado[clave])}]"
                f"{escape_markup(texto_estado)}[/color]"
            )

            if clave == "pendiente":
                texto_boton = "Ya está en pendientes"
                activo = False
            elif rec["etapa"] == "futuro":
                texto_boton = "Aún no se siembra"
                activo = False
            else:
                texto_boton = "Agregar a pendientes por regar"
                activo = True

            tarjeta = TarjetaCultivo(
                texto,
                texto_boton,
                lambda codigo=cultivo.codigo: self.programar_riego(codigo),
                activo
            )

            self.lista_tarjetas.add_widget(tarjeta)

    def _refrescar_cola(self):

        pendientes = self.planificador.cola.a_lista()

        if not pendientes:
            self.cuadro_cola.poner("No hay riegos pendientes.")
            return

        lineas = []

        for numero, codigo in enumerate(pendientes, 1):

            linea = f"{numero}. {self._nombre(codigo)} ({codigo})"

            if numero == 1:
                linea += "   <- el siguiente"

            lineas.append(linea)

        self.cuadro_cola.poner("\n".join(lineas))

    def _refrescar_historial(self):

        registros = self.planificador.historial.a_lista()

        if not registros:
            self.cuadro_historial.poner("Todavía no has anotado ningún riego.")
            return

        lineas = []

        for registro in registros[:10]:

            try:
                momento = datetime.strptime(
                    registro["momento"], "%Y-%m-%d %H:%M"
                ).strftime("%d/%m/%Y %H:%M")
            except (ValueError, KeyError):
                momento = str(registro.get("momento", ""))

            lineas.append(
                f"{momento}  -  {self._nombre(registro['codigo'])}"
            )

        if len(registros) > 10:
            lineas.append(f"... y {len(registros) - 10} riegos más antiguos")

        self.cuadro_historial.poner("\n".join(lineas))

    def _refrescar_canales(self):

        canales = self.planificador.canales

        if not canales:
            self.cuadro_canales.poner(
                "Todavía no hay conexiones. Empieza conectando el "
                "Tanque de agua con uno de tus cultivos."
            )
            return

        lineas = [
            f"{self._nombre_nodo(c['desde'])}  conectado con  "
            f"{self._nombre_nodo(c['hasta'])}  ({c['metros']:g} metros)"
            for c in canales
        ]

        self.cuadro_canales.poner("\n".join(lineas))

    def _refrescar_selectores(self):

        self.mapa_nodos = {"Tanque de agua": "TANQUE"}
        self.mapa_cultivos = {}

        for cultivo in self.gestor.lista_cultivos:

            etiqueta = f"{cultivo.nombre} ({cultivo.codigo})"

            self.mapa_nodos[etiqueta] = cultivo.codigo
            self.mapa_cultivos[etiqueta] = cultivo.codigo

        opciones = [
            (self.sp_desde, list(self.mapa_nodos), "Elige el punto de salida"),
            (self.sp_hasta, list(self.mapa_nodos), "Elige el punto de llegada"),
            (self.sp_destino, list(self.mapa_cultivos), "Elige un cultivo"),
        ]

        for spinner, valores, inicial in opciones:

            spinner.values = valores

            if spinner.text not in valores:
                spinner.text = inicial

    def _refrescar_total(self):

        cultivos = self.gestor.lista_cultivos

        if not cultivos:
            self.texto_total.text = (
                "Registra cultivos para poder repartir el agua."
            )
            return

        total = self.planificador.necesidad_total(cultivos)

        self.texto_total.text = (
            f"Para regar todos tus cultivos hoy necesitarías unos "
            f"{total:,.0f} litros. Escribe cuánta agua tienes y te "
            f"decimos cómo repartirla."
        )

    # ========================================================
    # ACCIONES: PENDIENTES
    # ========================================================

    def programar_riego(self, codigo):

        if not self.planificador.programar_riego(codigo):
            self._decir("Ese cultivo ya está en la lista de pendientes.", COLOR_INFO)
            return

        self._decir(
            f"Agregado a pendientes: {self._nombre(codigo)}.",
            COLOR_EXITO
        )

        self._refrescar_tarjetas()
        self._refrescar_cola()

    def atender_siguiente(self, *_):

        registro = self.planificador.atender_siguiente()

        if registro is None:
            self._decir("No hay riegos pendientes por anotar.", COLOR_INFO)
            return

        self._decir(
            f"Anotado: ya se regó {self._nombre(registro['codigo'])}.",
            COLOR_EXITO
        )

        self._refrescar_tarjetas()
        self._refrescar_cola()
        self._refrescar_historial()

    # ========================================================
    # ACCIONES: REPARTIR EL AGUA
    # ========================================================

    def repartir_agua(self, *_):

        try:
            litros = float(self.campo_agua.text.strip())
            if litros <= 0:
                raise ValueError
        except ValueError:
            self._decir(
                "Escribe cuántos litros de agua tienes (un número mayor que 0).",
                COLOR_ERROR
            )
            return

        cultivos = self.gestor.lista_cultivos

        if not cultivos:
            self._decir(
                "Primero registra cultivos en la pantalla Cultivos.",
                COLOR_ERROR
            )
            return

        resultado, sobrante = self.planificador.repartir_agua(cultivos, litros)

        if not resultado:
            self.cuadro_reparto.poner(
                "Tus cultivos todavía no se han sembrado, así que no "
                "necesitan agua por ahora."
            )
            return

        total = sum(item.necesidad for item in resultado)

        lineas = [
            f"Tienes {litros:,.0f} litros y necesitas {total:,.0f} para regar todo.",
            "Primero se riegan los cultivos más delicados y los que gastan "
            "menos agua, para que alcance para más cultivos.",
            ""
        ]

        for numero, item in enumerate(resultado, 1):

            if item.asignado >= item.necesidad - 0.5:
                veredicto = "riego completo"
            elif item.asignado > 0:
                veredicto = "riego parcial"
            else:
                veredicto = "sin agua por ahora"

            lineas.append(
                f"{numero}. {item.nombre} - {veredicto}\n"
                f"    Dale {item.asignado:,.0f} de {item.necesidad:,.0f} litros"
            )

        lineas.append("")

        if sobrante > 0.5:
            lineas.append(f"Te sobran {sobrante:,.0f} litros.")
        else:
            falta = total - litros
            lineas.append(f"Te faltan unos {falta:,.0f} litros para regar todo.")

        self.cuadro_reparto.poner("\n".join(lineas))

        self._decir("Listo, así puedes repartir tu agua.", COLOR_EXITO)

    # ========================================================
    # ACCIONES: CAMINO DEL AGUA
    # ========================================================

    def agregar_canal(self, *_):

        desde = self.mapa_nodos.get(self.sp_desde.text)
        hasta = self.mapa_nodos.get(self.sp_hasta.text)

        if desde is None or hasta is None:
            self._decir(
                "Elige los dos lugares que quieres conectar.",
                COLOR_ERROR
            )
            return

        if desde == hasta:
            self._decir(
                "Los dos lugares deben ser distintos.",
                COLOR_ERROR
            )
            return

        try:
            metros = float(self.campo_metros.text.strip())
            if metros <= 0:
                raise ValueError
        except ValueError:
            self._decir(
                "La distancia debe ser un número mayor que 0.",
                COLOR_ERROR
            )
            return

        self.planificador.agregar_canal(desde, hasta, metros)

        self.campo_metros.text = ""
        self.sp_desde.text = "Elige el punto de salida"
        self.sp_hasta.text = "Elige el punto de llegada"

        self._decir(
            f"Conexión guardada: {self._nombre_nodo(desde)} y "
            f"{self._nombre_nodo(hasta)} ({metros:g} metros).",
            COLOR_EXITO
        )

        self._refrescar_canales()

    def borrar_canales(self, *_):

        self.planificador.borrar_canales()

        self.cuadro_ruta.poner("Aquí aparecerá el camino más corto.")

        self._decir("Se borraron todas las conexiones.", COLOR_INFO)

        self._refrescar_canales()

    def calcular_ruta(self, *_):

        destino = self.mapa_cultivos.get(self.sp_destino.text)

        if destino is None:
            self._decir("Elige primero un cultivo.", COLOR_ERROR)
            return

        distancia, camino = self.planificador.ruta_mas_corta(destino)

        if distancia is None:
            self.cuadro_ruta.poner(
                "Todavía no hay conexiones que lleguen del tanque a ese "
                "cultivo. Agrega las que faltan en el Paso A."
            )
            self._decir("No se encontró un camino.", COLOR_ERROR)
            return

        nombres = "  ->  ".join(self._nombre_nodo(nodo) for nodo in camino)

        self.cuadro_ruta.poner(
            f"Camino más corto:\n{nombres}\n\n"
            f"Distancia total: {distancia:g} metros"
        )

        self._decir("Camino calculado.", COLOR_EXITO)


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

if __name__ == "__main__":

    from kivy.app import App

    class PruebaOptimizacion(App):

        def build(self):

            return PantallaOptimizacion()

    PruebaOptimizacion().run()