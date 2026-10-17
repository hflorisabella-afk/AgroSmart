import os
import sys
from datetime import date, datetime

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

RUTA_MODELOS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "modelos")
)
if RUTA_MODELOS not in sys.path:
    sys.path.append(RUTA_MODELOS)

from inventario import InventarioDiseño

COLOR_FONDO = (0.18, 0.16, 0.08, 1)
COLOR_AMARILLO = (0.90, 0.78, 0.42, 1)
COLOR_AMARILLO_PRINCIPAL = COLOR_AMARILLO
COLOR_TEXTO = (0.97, 0.95, 0.87, 1)
COLOR_TARJETA = (0.28, 0.25, 0.15, 1)
COLOR_ALERTA = (0.70, 0.25, 0.18, 1)
COLOR_AVISO = (0.80, 0.53, 0.16, 1)
COLOR_NORMAL = (0.28, 0.42, 0.25, 1)

STOCK_BAJO = 5
DIAS_PARA_VENCER = 7


class TarjetaAlerta(BoxLayout):
    def __init__(self, titulo, detalle, color, **kwargs):
        super().__init__(
            orientation="vertical", size_hint_y=None, height=dp(66),
            padding=[dp(12), dp(7)], spacing=dp(2), **kwargs
        )
        with self.canvas.before:
            Color(*color)
            self.fondo = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(9)])
        self.bind(pos=self.actualizar_fondo, size=self.actualizar_fondo)

        self.titulo = Label(
            text=titulo, color=(1, 1, 1, 1), bold=True, font_size="14sp",
            halign="left", valign="middle", size_hint_y=None, height=dp(23)
        )
        self.detalle = Label(
            text=detalle, color=(1, 1, 1, 1), font_size="12sp",
            halign="left", valign="middle"
        )
        self.add_widget(self.titulo)
        self.add_widget(self.detalle)
        self.bind(size=self.ajustar_texto)
        self.ajustar_texto()

    def ajustar_texto(self, *_):
        ancho = max(1, self.width - dp(24))
        self.titulo.text_size = (ancho, None)
        self.detalle.text_size = (ancho, None)

    def actualizar_fondo(self, *_):
        self.fondo.pos = self.pos
        self.fondo.size = self.size


class PantallaInventario(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        with self.canvas.before:
            Color(*COLOR_FONDO)
            self.rectangulo = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.actualizar_fondo, size=self.actualizar_fondo)

        encabezado = BoxLayout(
            orientation="vertical", size_hint_y=None, height=dp(68),
            padding=[dp(12), dp(7)], spacing=dp(2)
        )
        encabezado.add_widget(Label(
            text="Inventario", color=COLOR_AMARILLO, bold=True,
            font_size="22sp", halign="center", valign="middle"
        ))
        encabezado.add_widget(Label(
            text="Existencias y fechas de vencimiento",
            color=COLOR_TEXTO, font_size="13sp",
            halign="center", valign="middle"
        ))
        self.add_widget(encabezado)

        self.resumen = Label(
            text="Alertas de inventario", color=COLOR_TEXTO,
            font_size="14sp", size_hint_y=None, height=dp(28),
            halign="left", valign="middle"
        )
        self.add_widget(self.resumen)

        self.scroll_alertas = ScrollView(
            size_hint_y=None, height=dp(165), do_scroll_x=False
        )
        self.contenedor_alertas = BoxLayout(
            orientation="vertical", size_hint_y=None,
            spacing=dp(6), padding=[dp(8), dp(4)]
        )
        self.contenedor_alertas.bind(
            minimum_height=self.contenedor_alertas.setter("height")
        )
        self.scroll_alertas.add_widget(self.contenedor_alertas)
        self.add_widget(self.scroll_alertas)

        self.inventario = InventarioDiseño()
        self.inventario.on_change = self.actualizar_alertas
        self.add_widget(self.inventario)

        Clock.schedule_once(lambda *_: self.actualizar_alertas(), 0.2)
        Clock.schedule_interval(lambda *_: self.actualizar_alertas(), 60)

    def actualizar_fondo(self, *_):
        self.rectangulo.pos = self.pos
        self.rectangulo.size = self.size

    def actualizar_lista(self):
        self.inventario.mostrar_productos()
        self.actualizar_alertas()

    def actualizar_alertas(self, *_):
        hoy = date.today()
        alertas = []

        # Conexión directa con la lista real de InventarioDiseño.
        for producto in self.inventario.productos:
            nombre = producto.get("nombre", "Producto sin nombre")
            cantidad = int(producto.get("cantidad", 0))

            if cantidad <= 0:
                alertas.append((
                    "Producto agotado",
                    f"{nombre}: no quedan unidades.",
                    COLOR_ALERTA
                ))
            elif cantidad <= STOCK_BAJO:
                alertas.append((
                    "Quedan pocas unidades",
                    f"{nombre}: quedan {cantidad} unidades.",
                    COLOR_AVISO
                ))

            fecha_texto = producto.get("fecha_vencimiento", "")
            if fecha_texto:
                try:
                    vencimiento = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
                    dias = (vencimiento - hoy).days
                    fecha_es = vencimiento.strftime("%d/%m/%Y")
                    if dias < 0:
                        alertas.append((
                            "Producto vencido",
                            f"{nombre}: venció el {fecha_es}.",
                            COLOR_ALERTA
                        ))
                    elif dias <= DIAS_PARA_VENCER:
                        if dias == 0:
                            detalle = f"{nombre}: vence hoy ({fecha_es})."
                        elif dias == 1:
                            detalle = f"{nombre}: vence mañana ({fecha_es})."
                        else:
                            detalle = f"{nombre}: vence en {dias} días ({fecha_es})."
                        alertas.append((
                            "Producto próximo a vencer",
                            detalle,
                            COLOR_AVISO
                        ))
                except ValueError:
                    alertas.append((
                        "Fecha por revisar",
                        f"{nombre}: revisa la fecha de vencimiento registrada.",
                        COLOR_AVISO
                    ))

        self.contenedor_alertas.clear_widgets()
        if not alertas:
            self.resumen.text = "Todo en orden: no hay alertas detectadas."
            self.contenedor_alertas.add_widget(TarjetaAlerta(
                "Inventario al día",
                "Las alertas aparecerán aquí cuando el stock sea bajo o se acerque el vencimiento.",
                COLOR_NORMAL
            ))
            return

        self.resumen.text = f"Alertas detectadas: {len(alertas)}"
        for titulo, detalle, color in alertas:
            self.contenedor_alertas.add_widget(
                TarjetaAlerta(titulo, detalle, color)
            )
