import os
import sys

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


# ============================================================
# IMPORTAR INVENTARIO
# ============================================================

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "modelos"
    )
)

from inventario import InventarioDiseño


# ============================================================
# COLORES PARA APP PRINCIPAL
# ============================================================

COLOR_FONDO = (0.18, 0.16, 0.08, 1)

COLOR_AMARILLO_PRINCIPAL = (0.90, 0.78, 0.42, 1)

COLOR_AMARILLO_CLARO = (0.98, 0.89, 0.58, 1)

COLOR_TEXTO = (0.97, 0.95, 0.87, 1)

COLOR_TARJETA = (0.28, 0.25, 0.15, 1)


# ============================================================
# PANTALLA INVENTARIO
# ============================================================

class PantallaInventario(BoxLayout):

    def __init__(self, **kwargs):

        super().__init__(
            orientation="vertical",
            **kwargs
        )

        # ====================================================
        # FONDO
        # ====================================================

        with self.canvas.before:

            Color(*COLOR_FONDO)

            self.rectangulo = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

        self.bind(
            pos=self.actualizar_fondo,
            size=self.actualizar_fondo
        )

        # ====================================================
        # INVENTARIO DE TU COMPAÑERO
        # ====================================================

        self.inventario = InventarioDiseño()

        self.add_widget(
            self.inventario
        )

    # ========================================================
    # FONDO
    # ========================================================

    def actualizar_fondo(
        self,
        instancia,
        valor
    ):

        self.rectangulo.pos = self.pos
        self.rectangulo.size = self.size

    # ========================================================
    # ACTUALIZAR LISTA
    # ========================================================

    def actualizar_lista(self):

        self.inventario.mostrar_productos()