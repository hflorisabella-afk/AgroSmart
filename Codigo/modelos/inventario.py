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


# ============================================================
# INVENTARIO
# ============================================================

class InventarioDiseño(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        self.productos = []

        # ====================================================
        # FONDO
        # ====================================================

        with self.canvas.before:
            Color(*COLOR_FONDO)

            self.rectangulo_fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ====================================================
        # TÍTULO
        # ====================================================

        titulo = Label(
            text="INVENTARIO",
            font_size=24,
            bold=True,
            color=COLOR_AMARILLO_CLARO,
            size_hint_y=None,
            height=50
        )

        self.add_widget(titulo)

        subtitulo = Label(
            text="Administra tus productos y recursos",
            font_size=14,
            color=COLOR_TEXTO_SECUNDARIO,
            size_hint_y=None,
            height=30
        )

        self.add_widget(subtitulo)

        # ====================================================
        # NOMBRE DEL PRODUCTO
        # ====================================================

        self.nombre_producto = TextInput(
            hint_text="Nombre del producto",
            multiline=False,
            size_hint_y=None,
            height=45,
            background_normal="",
            background_active="",
            background_color=(0.96, 0.92, 0.76, 1),
            foreground_color=(0.15, 0.14, 0.10, 1),
            hint_text_color=(0.45, 0.43, 0.35, 1),
            padding=[15, 12, 15, 12]
        )

        self.add_widget(
            self.nombre_producto
        )

        # ====================================================
        # CANTIDAD
        # ====================================================

        self.cantidad_producto = TextInput(
            hint_text="Cantidad del producto",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=45,
            background_normal="",
            background_active="",
            background_color=(0.96, 0.92, 0.76, 1),
            foreground_color=(0.15, 0.14, 0.10, 1),
            hint_text_color=(0.45, 0.43, 0.35, 1),
            padding=[15, 12, 15, 12]
        )

        self.add_widget(
            self.cantidad_producto
        )

        # ====================================================
        # TIPO
        # ====================================================

        self.tipo_producto = TextInput(
            hint_text="Tipo de producto",
            multiline=False,
            size_hint_y=None,
            height=45,
            background_normal="",
            background_active="",
            background_color=(0.96, 0.92, 0.76, 1),
            foreground_color=(0.15, 0.14, 0.10, 1),
            hint_text_color=(0.45, 0.43, 0.35, 1),
            padding=[15, 12, 15, 12]
        )

        self.add_widget(
            self.tipo_producto
        )

        # ====================================================
        # BOTONES
        # ====================================================

        botones = BoxLayout(
            orientation="horizontal",
            spacing=8,
            size_hint_y=None,
            height=50
        )

        boton_registrar = Button(
            text="Registrar",
            background_normal="",
            background_color=COLOR_AMARILLO,
            color=(0.12, 0.11, 0.07, 1),
            bold=True
        )

        boton_mostrar = Button(
            text="Mostrar",
            background_normal="",
            background_color=COLOR_TARJETA_CLARA,
            color=COLOR_TEXTO,
            bold=True
        )

        boton_eliminar = Button(
            text="Eliminar",
            background_normal="",
            background_color=(0.55, 0.30, 0.25, 1),
            color=COLOR_TEXTO,
            bold=True
        )

        boton_registrar.bind(
            on_release=self.registrar_producto
        )

        boton_mostrar.bind(
            on_release=self.mostrar_productos
        )

        boton_eliminar.bind(
            on_release=self.eliminar_producto
        )

        botones.add_widget(
            boton_registrar
        )

        botones.add_widget(
            boton_mostrar
        )

        botones.add_widget(
            boton_eliminar
        )

        self.add_widget(
            botones
        )

        # ====================================================
        # TÍTULO DE LA LISTA
        # ====================================================

        titulo_lista = Label(
            text="INVENTARIO ACTUAL",
            font_size=18,
            bold=True,
            color=COLOR_AMARILLO_CLARO,
            size_hint_y=None,
            height=40
        )

        self.add_widget(
            titulo_lista
        )

        # ====================================================
        # LISTA
        # ====================================================

        self.lista_productos = Label(
            text="No hay productos registrados.",
            color=COLOR_TEXTO,
            font_size=14,
            halign="left",
            valign="top",
            size_hint_y=None
        )

        self.lista_productos.bind(
            texture_size=self.actualizar_altura
        )

        scroll = ScrollView(
            do_scroll_x=False
        )

        scroll.add_widget(
            self.lista_productos
        )

        self.add_widget(
            scroll
        )

    # ========================================================
    # ACTUALIZAR FONDO
    # ========================================================

    def actualizar_fondo(
        self,
        instancia,
        valor
    ):

        self.rectangulo_fondo.pos = self.pos
        self.rectangulo_fondo.size = self.size

    # ========================================================
    # ACTUALIZAR ALTURA
    # ========================================================

    def actualizar_altura(
        self,
        instancia,
        tamaño
    ):

        self.lista_productos.height = max(
            tamaño[1],
            100
        )

    # ========================================================
    # REGISTRAR PRODUCTO
    # ========================================================

    def registrar_producto(
        self,
        instancia
    ):

        nombre = self.nombre_producto.text.strip()
        cantidad = self.cantidad_producto.text.strip()
        tipo = self.tipo_producto.text.strip()

        if not nombre or not cantidad or not tipo:

            self.mostrar_mensaje(
                "Error",
                "Por favor, completa todos los campos."
            )

            return

        try:

            cantidad = int(cantidad)

        except ValueError:

            self.mostrar_mensaje(
                "Error",
                "La cantidad debe ser un número entero."
            )

            return

        if cantidad <= 0:

            self.mostrar_mensaje(
                "Error",
                "La cantidad debe ser mayor que cero."
            )

            return

        producto = {
            "nombre": nombre,
            "cantidad": cantidad,
            "tipo": tipo
        }

        self.productos.append(
            producto
        )

        self.nombre_producto.text = ""
        self.cantidad_producto.text = ""
        self.tipo_producto.text = ""

        self.mostrar_productos()

        self.mostrar_mensaje(
            "Registro exitoso",
            "El producto se registró correctamente."
        )

    # ========================================================
    # MOSTRAR PRODUCTOS
    # ========================================================

    def mostrar_productos(
        self,
        instancia=None
    ):

        if not self.productos:

            self.lista_productos.text = (
                "No hay productos registrados."
            )

            return

        texto = "LISTA DE INVENTARIO\n\n"

        for numero, producto in enumerate(
            self.productos,
            1
        ):

            texto += (
                f"{numero}. {producto['nombre']}\n"
                f"   Cantidad: {producto['cantidad']}\n"
                f"   Tipo: {producto['tipo']}\n\n"
            )

        self.lista_productos.text = texto

    # ========================================================
    # ELIMINAR PRODUCTO
    # ========================================================

    def eliminar_producto(
        self,
        instancia
    ):

        if not self.productos:

            self.mostrar_mensaje(
                "Aviso",
                "No hay productos registrados para eliminar."
            )

            return

        producto = self.productos.pop()

        self.mostrar_productos()

        self.mostrar_mensaje(
            "Producto eliminado",
            f"Se eliminó el producto: "
            f"{producto['nombre']}"
        )

    # ========================================================
    # MOSTRAR MENSAJE
    # ========================================================

    def mostrar_mensaje(
        self,
        titulo,
        texto
    ):

        contenido = BoxLayout(
            orientation="vertical",
            padding=10,
            spacing=10
        )

        mensaje = Label(
            text=texto,
            color=COLOR_TEXTO,
            halign="center",
            valign="middle"
        )

        boton_aceptar = Button(
            text="Aceptar",
            size_hint_y=None,
            height=45,
            background_normal="",
            background_color=COLOR_AMARILLO,
            color=(0.12, 0.11, 0.07, 1),
            bold=True
        )

        contenido.add_widget(
            mensaje
        )

        contenido.add_widget(
            boton_aceptar
        )

        ventana = Popup(
            title=titulo,
            content=contenido,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        boton_aceptar.bind(
            on_release=ventana.dismiss
        )

        ventana.open()


# ============================================================
# PRUEBA INDIVIDUAL
# ============================================================

class AgroSmartAplicacion(App):

    def build(self):

        return InventarioDiseño()


if __name__ == "__main__":

    AgroSmartAplicacion().run()