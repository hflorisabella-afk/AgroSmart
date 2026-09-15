# pantalla_riego.py
# Pantalla visual para el Sistema de Riego Inteligente de AgroSmart.
# Este módulo es independiente (tiene su propia clase Cultivo, separada de
# la del módulo de Registro de Cultivos) — por eso vive en su propia carpeta,
# junto a riego_agrosmart.py.
#
# Permite: registrar un cultivo para riego, ver todos con su estado actual,
# ejecutar la revisión/riego automático, y eliminar un cultivo.

from datetime import datetime

from riego_agrosmart import (
    Cultivo, GestorRiego, ControladorRiego, PROVEEDOR_CLIMA, normalizar_codigo,
)

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# ================= COLORES DEL TEMA (igual que las otras pantallas) =================
COLOR_FONDO = (0.06, 0.1, 0.08, 1)
COLOR_VERDE_PRINCIPAL = (0.29, 0.49, 0.36, 1)
COLOR_VERDE_CLARO = (0.65, 0.85, 0.6, 1)
COLOR_TEXTO_CLARO = (0.92, 0.95, 0.9, 1)
COLOR_CAJA_TEXTO = (0.95, 0.97, 0.94, 1)
COLOR_ERROR = (1, 0.55, 0.5, 1)
COLOR_EXITO = (0.55, 0.9, 0.5, 1)
COLOR_INFO = (0.6, 0.8, 0.9, 1)
COLOR_AZUL_RIEGO = (0.25, 0.45, 0.6, 1)

Window.clearcolor = COLOR_FONDO
Window.size = (780, 850)

gestor = GestorRiego()
ALTURA_FILA = 45


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


def fila_con_etiqueta(texto_etiqueta, hint=""):
    fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=ALTURA_FILA, spacing=10)
    etiqueta = Label(text=texto_etiqueta, size_hint=(0.4, 1), font_size=16,
                      halign="right", valign="middle", color=COLOR_TEXTO_CLARO)
    etiqueta.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    fila.add_widget(etiqueta)
    caja = caja_de_texto(hint)
    fila.add_widget(caja)
    return fila, caja


class PantallaRiego(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        contenido = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        contenido.bind(minimum_height=contenido.setter("height"))
        self.add_widget(contenido)

        titulo = Label(text="AgroSmart - Sistema de Riego", font_size=24, bold=True,
                        size_hint_y=None, height=45, color=COLOR_VERDE_CLARO)
        contenido.add_widget(titulo)

        # --- Formulario de registro ---
        fila, self.campo_nombre = fila_con_etiqueta("Nombre del cultivo:", "ej: Maíz parcela 5")
        contenido.add_widget(fila)
        fila, self.campo_tipo = fila_con_etiqueta("Tipo de cultivo:", "ej: Maíz, Frijol, Café")
        contenido.add_widget(fila)
        fila, self.campo_tierra = fila_con_etiqueta("Tipo de tierra:", "ej: Arcillosa, Arenosa")
        contenido.add_widget(fila)
        fila, self.campo_localidad = fila_con_etiqueta("Localidad:", "ej: Chimaltenango")
        contenido.add_widget(fila)
        fila, self.campo_parcela = fila_con_etiqueta("Número de parcela:", "ej: 3")
        contenido.add_widget(fila)
        fila, self.campo_tamano = fila_con_etiqueta("Tamaño de parcela (ha):", "ej: 2.5")
        contenido.add_widget(fila)
        fila, self.campo_fecha = fila_con_etiqueta("Fecha de siembra (AAAA-MM-DD):", "ej: 2026-08-19")
        contenido.add_widget(fila)

        boton_registrar = boton_estilizado("Registrar cultivo para riego")
        boton_registrar.bind(on_press=self.registrar_cultivo)
        contenido.add_widget(boton_registrar)

        self.mensaje = Label(text="", size_hint_y=None, height=30, color=COLOR_ERROR)
        contenido.add_widget(self.mensaje)

        # --- Acción principal: revisar y regar ---
        boton_revisar = boton_estilizado("Revisar y regar todos los cultivos", color_fondo=COLOR_AZUL_RIEGO)
        boton_revisar.bind(on_press=self.revisar_y_regar)
        contenido.add_widget(boton_revisar)

        self.mensaje_riego = Label(text="", size_hint_y=None, height=50, color=COLOR_INFO)
        contenido.add_widget(self.mensaje_riego)

        # --- Eliminar ---
        fila, self.campo_codigo_eliminar = fila_con_etiqueta("Código a eliminar:", "ej: CULT001")
        contenido.add_widget(fila)
        boton_eliminar = boton_estilizado("Eliminar cultivo", color_fondo=(0.55, 0.25, 0.22, 1))
        boton_eliminar.bind(on_press=self.eliminar_cultivo)
        contenido.add_widget(boton_eliminar)

        # --- Lista de cultivos y su estado ---
        contenido.add_widget(Label(text="Cultivos y su estado de riego:", size_hint_y=None, height=30,
                                    font_size=16, color=COLOR_VERDE_CLARO, bold=True))
        self.lista_texto = Label(text="", size_hint_y=None, halign="left", valign="top",
                                  font_size=13, color=COLOR_TEXTO_CLARO)
        self.lista_texto.bind(texture_size=self._actualizar_altura_lista)
        contenido.add_widget(self.lista_texto)

        self.actualizar_lista()

    def _actualizar_altura_lista(self, instancia, tamano):
        instancia.height = tamano[1]
        instancia.text_size = (instancia.width, None)

    def registrar_cultivo(self, instancia_boton):
        nombre = self.campo_nombre.text.strip()
        tipo = self.campo_tipo.text.strip()
        tierra = self.campo_tierra.text.strip()
        localidad = self.campo_localidad.text.strip()
        parcela = self.campo_parcela.text.strip()
        tamano_texto = self.campo_tamano.text.strip()
        fecha = self.campo_fecha.text.strip()

        if not nombre or not tipo or not tierra or not localidad or not parcela:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Todos los campos son obligatorios."
            return

        try:
            tamano = float(tamano_texto)
            if tamano <= 0:
                self.mensaje.color = COLOR_ERROR
                self.mensaje.text = "El tamaño debe ser mayor a 0."
                return
        except ValueError:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "El tamaño debe ser un número, ej. 2.5."
            return

        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Fecha inválida. Usa el formato AAAA-MM-DD."
            return

        cultivo = Cultivo(
            codigo=gestor.generar_codigo(), nombre=nombre, tipo=tipo,
            tipo_tierra=tierra, localidad=localidad, numero_parcela=parcela,
            tamano_parcela=tamano, fecha_siembra=fecha,
        )
        zona = gestor.registrar_cultivo(cultivo)

        self.mensaje.color = COLOR_EXITO
        self.mensaje.text = (f"Cultivo '{nombre}' registrado ({cultivo.codigo}) - "
                              f"etapa: {zona.config.etapa_crecimiento}")

        self.campo_nombre.text = ""
        self.campo_tipo.text = ""
        self.campo_tierra.text = ""
        self.campo_localidad.text = ""
        self.campo_parcela.text = ""
        self.campo_tamano.text = ""
        self.campo_fecha.text = ""

        self.actualizar_lista()

    def revisar_y_regar(self, instancia_boton):
        if not gestor.zonas:
            self.mensaje_riego.color = COLOR_ERROR
            self.mensaje_riego.text = "No hay cultivos registrados todavía."
            return

        controlador = ControladorRiego(gestor=gestor, proveedor_clima=PROVEEDOR_CLIMA)
        pronostico = PROVEEDOR_CLIMA.obtener_pronostico()

        controlador.revisar_y_regar_todas()

        self.mensaje_riego.color = COLOR_INFO
        self.mensaje_riego.text = (
            f"Pronóstico usado: {pronostico.probabilidad_lluvia*100:.0f}% prob. lluvia, "
            f"{pronostico.mm_lluvia_esperada}mm, {pronostico.temperatura_c}°C.\n"
            f"Revisión completada — mira el estado actualizado de cada cultivo abajo."
        )
        self.actualizar_lista()

    def eliminar_cultivo(self, instancia_boton):
        codigo_texto = self.campo_codigo_eliminar.text.strip()

        if not codigo_texto:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Escribe el código del cultivo a eliminar."
            return

        codigo_normalizado = normalizar_codigo(codigo_texto)
        zona_encontrada = gestor.buscar_por_codigo(codigo_normalizado)

        if zona_encontrada is None:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = f"No existe ningún cultivo con el código '{codigo_normalizado}'."
            return

        nombre_eliminado = zona_encontrada.cultivo.nombre
        gestor.eliminar_cultivo(codigo_normalizado)
        self.mensaje.color = COLOR_EXITO
        self.mensaje.text = f"Cultivo '{nombre_eliminado}' ({codigo_normalizado}) eliminado."
        self.campo_codigo_eliminar.text = ""
        self.actualizar_lista()

    def actualizar_lista(self):
        gestor.recalcular_configuraciones()
        if len(gestor.zonas) == 0:
            self.lista_texto.text = "No hay cultivos registrados todavía."
        else:
            lineas = [str(zona) for zona in gestor.zonas.values()]
            self.lista_texto.text = "\n".join(lineas)


class AgroSmartRiegoApp(App):
    def build(self):
        self.title = "AgroSmart - Riego"
        return PantallaRiego()


if __name__ == "__main__":
    AgroSmartRiegoApp().run()