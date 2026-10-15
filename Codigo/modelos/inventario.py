from datetime import date, datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle


# ============================================================
# COLORES
# ============================================================

COLOR_FONDO = (0.18, 0.16, 0.08, 1)
COLOR_AMARILLO = (0.90, 0.78, 0.42, 1)
COLOR_AMARILLO_CLARO = (0.98, 0.89, 0.58, 1)
COLOR_TEXTO = (0.97, 0.95, 0.87, 1)
COLOR_TEXTO_SECUNDARIO = (0.76, 0.72, 0.60, 1)
COLOR_TARJETA = (0.28, 0.25, 0.15, 1)
COLOR_TARJETA_CLARA = (0.36, 0.32, 0.19, 1)
COLOR_EXITO = (0.55, 0.82, 0.55, 1)
COLOR_ERROR = (0.95, 0.50, 0.45, 1)


class InventarioDiseño(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10
        self.productos = []
        self.on_change = None

        with self.canvas.before:
            Color(*COLOR_FONDO)
            self.rectangulo_fondo = RoundedRectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.actualizar_fondo, size=self.actualizar_fondo)

        self.add_widget(Label(
            text="INVENTARIO", font_size=24, bold=True,
            color=COLOR_AMARILLO_CLARO, size_hint_y=None, height=50
        ))
        self.add_widget(Label(
            text="Administra tus productos y recursos", font_size=14,
            color=COLOR_TEXTO_SECUNDARIO, size_hint_y=None, height=30
        ))

        self.nombre_producto = self.crear_campo("Nombre del producto")
        self.cantidad_producto = self.crear_campo(
            "Cantidad del producto", input_filter="int"
        )
        self.tipo_producto = self.crear_campo("Tipo de producto")
        self.fecha_vencimiento = self.crear_campo(
            "Fecha de vencimiento (AAAA-MM-DD; opcional)"
        )

        botones = BoxLayout(
            orientation="horizontal", spacing=8,
            size_hint_y=None, height=50
        )
        for texto, color, accion, color_texto in [
            ("Registrar", COLOR_AMARILLO, self.registrar_producto, (0.12, 0.11, 0.07, 1)),
            ("Mostrar", COLOR_TARJETA_CLARA, self.mostrar_productos, COLOR_TEXTO),
            ("Eliminar último", (0.55, 0.30, 0.25, 1), self.eliminar_producto, COLOR_TEXTO),
        ]:
            boton = Button(
                text=texto, background_normal="", background_color=color,
                color=color_texto, bold=True
            )
            boton.bind(on_release=accion)
            botones.add_widget(boton)
        self.add_widget(botones)

        self.add_widget(Label(
            text="INVENTARIO ACTUAL", font_size=18, bold=True,
            color=COLOR_AMARILLO_CLARO, size_hint_y=None, height=40
        ))

        self.lista_productos = Label(
            text="No hay productos registrados.", color=COLOR_TEXTO,
            font_size=14, halign="left", valign="top",
            size_hint_y=None
        )
        self.lista_productos.bind(
            texture_size=self.actualizar_altura,
            width=lambda *_: self.ajustar_ancho_lista()
        )
        scroll = ScrollView(do_scroll_x=False)
        scroll.add_widget(self.lista_productos)
        self.add_widget(scroll)

    def crear_campo(self, texto, input_filter=None):
        campo = TextInput(
            hint_text=texto, multiline=False, input_filter=input_filter,
            size_hint_y=None, height=45,
            background_normal="", background_active="",
            background_color=(0.96, 0.92, 0.76, 1),
            foreground_color=(0.15, 0.14, 0.10, 1),
            hint_text_color=(0.45, 0.43, 0.35, 1),
            padding=[15, 12, 15, 12]
        )
        self.add_widget(campo)
        return campo

    def actualizar_fondo(self, *_):
        self.rectangulo_fondo.pos = self.pos
        self.rectangulo_fondo.size = self.size

    def ajustar_ancho_lista(self):
        self.lista_productos.text_size = (max(1, self.lista_productos.width), None)

    def actualizar_altura(self, _, tamaño):
        self.lista_productos.height = max(tamaño[1], 100)

    def registrar_producto(self, *_):
        nombre = self.nombre_producto.text.strip()
        cantidad_texto = self.cantidad_producto.text.strip()
        tipo = self.tipo_producto.text.strip()
        fecha_texto = self.fecha_vencimiento.text.strip()

        if not nombre or not cantidad_texto or not tipo:
            self.mostrar_mensaje("Faltan datos", "Completa nombre, cantidad y tipo de producto.")
            return

        try:
            cantidad = int(cantidad_texto)
        except ValueError:
            self.mostrar_mensaje("Cantidad inválida", "La cantidad debe ser un número entero.")
            return

        if cantidad < 0:
            self.mostrar_mensaje("Cantidad inválida", "La cantidad no puede ser negativa.")
            return

        fecha_iso = ""
        if fecha_texto:
            try:
                fecha_iso = datetime.strptime(fecha_texto, "%Y-%m-%d").date().isoformat()
            except ValueError:
                self.mostrar_mensaje(
                    "Fecha inválida",
                    "Escribe la fecha como AAAA-MM-DD, por ejemplo 2026-12-31."
                )
                return

        producto = {
            "nombre": nombre,
            "cantidad": cantidad,
            "tipo": tipo,
            "fecha_vencimiento": fecha_iso
        }
        self.productos.append(producto)

        self.nombre_producto.text = ""
        self.cantidad_producto.text = ""
        self.tipo_producto.text = ""
        self.fecha_vencimiento.text = ""
        self.mostrar_productos()
        self.notificar_cambio()
        self.mostrar_mensaje("Registro exitoso", "El producto se registró correctamente.")

    def mostrar_productos(self, *_):
        if not self.productos:
            self.lista_productos.text = "No hay productos registrados."
            return

        lineas = ["LISTA DE INVENTARIO", ""]
        for numero, producto in enumerate(self.productos, 1):
            fecha = producto.get("fecha_vencimiento") or "No indicada"
            if fecha != "No indicada":
                try:
                    fecha = datetime.strptime(fecha, "%Y-%m-%d").strftime("%d/%m/%Y")
                except ValueError:
                    pass
            lineas.append(
                f"{numero}. {producto['nombre']}\n"
                f"   Cantidad: {producto['cantidad']}\n"
                f"   Tipo: {producto['tipo']}\n"
                f"   Vencimiento: {fecha}\n"
            )
        self.lista_productos.text = "\n".join(lineas)
        self.ajustar_ancho_lista()

    def eliminar_producto(self, *_):
        if not self.productos:
            self.mostrar_mensaje("Aviso", "No hay productos registrados para eliminar.")
            return
        producto = self.productos.pop()
        self.mostrar_productos()
        self.notificar_cambio()
        self.mostrar_mensaje("Producto eliminado", f"Se eliminó: {producto['nombre']}.")

    def notificar_cambio(self):
        if callable(self.on_change):
            self.on_change()

    def mostrar_mensaje(self, titulo, texto):
        contenido = BoxLayout(orientation="vertical", padding=10, spacing=10)
        contenido.add_widget(Label(text=texto, color=COLOR_TEXTO, halign="center", valign="middle"))
        boton = Button(
            text="Aceptar", size_hint_y=None, height=45,
            background_normal="", background_color=COLOR_AMARILLO,
            color=(0.12, 0.11, 0.07, 1), bold=True
        )
        contenido.add_widget(boton)
        ventana = Popup(
            title=titulo, content=contenido, size_hint=(0.8, 0.4),
            auto_dismiss=False, separator_color=COLOR_AMARILLO
        )
        boton.bind(on_release=ventana.dismiss)
        ventana.open()


class AgroSmartAplicacion(App):
    def build(self):
        return InventarioDiseño()


if __name__ == "__main__":
    AgroSmartAplicacion().run()
