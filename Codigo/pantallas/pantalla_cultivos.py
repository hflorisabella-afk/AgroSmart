# pantalla_cultivos.py
# Pantalla visual de AgroSmart para el módulo de Registro de Cultivos.
# Permite: registrar, buscar (por nombre, tipo o parcela), seleccionar un
# resultado para editarlo o eliminarlo, y ordenar por fecha de siembra.
#
# Toda la lógica "de fondo" (guardar, validar, etc.) vive en
# modelos/cultivo.py y modelos/gestor_cultivos.py — aquí solo conectamos
# esa lógica con botones y cajas de texto en pantalla.

import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modelos"))

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# ================= COLORES DEL TEMA (verde agrícola) =================
COLOR_FONDO = (0.06, 0.1, 0.08, 1)          # verde muy oscuro, casi negro
COLOR_VERDE_PRINCIPAL = (0.29, 0.49, 0.36, 1)  # verde medio, para botones
COLOR_VERDE_CLARO = (0.65, 0.85, 0.6, 1)    # verde clarito, para títulos y textos destacados
COLOR_TEXTO_CLARO = (0.92, 0.95, 0.9, 1)    # casi blanco con tinte verde, para texto normal
COLOR_CAJA_TEXTO = (0.95, 0.97, 0.94, 1)    # crema clarito, fondo de las cajas de texto
COLOR_ERROR = (1, 0.55, 0.5, 1)
COLOR_EXITO = (0.55, 0.9, 0.5, 1)
COLOR_INFO = (0.6, 0.8, 0.9, 1)

Window.clearcolor = COLOR_FONDO
Window.size = (780, 850)

gestor = GestorCultivos()

ALTURA_FILA = 45


def caja_de_texto(hint=""):
    # Crea una caja de texto con el estilo del tema (fondo crema, letra oscura)
    return TextInput(
        multiline=False,
        hint_text=hint,
        font_size=17,
        padding=[10, 10, 10, 10],
        background_color=COLOR_CAJA_TEXTO,
        foreground_color=(0.1, 0.1, 0.1, 1),
        hint_text_color=(0.45, 0.45, 0.45, 1),
        size_hint=(0.6, 1),
    )


def boton_estilizado(texto, alto=45, color_fondo=None):
    # Crea un botón con el estilo del tema (verde, letra clara)
    boton = Button(
        text=texto,
        size_hint_y=None,
        height=alto,
        background_normal="",
        background_color=color_fondo if color_fondo else COLOR_VERDE_PRINCIPAL,
        color=(1, 1, 1, 1),
        bold=True,
    )
    return boton


def fila_con_etiqueta(texto_etiqueta, hint=""):
    fila = BoxLayout(orientation="horizontal", size_hint_y=None, height=ALTURA_FILA, spacing=10)
    etiqueta = Label(text=texto_etiqueta, size_hint=(0.4, 1), font_size=16,
                      halign="right", valign="middle", color=COLOR_TEXTO_CLARO)
    etiqueta.bind(size=lambda inst, val: setattr(inst, "text_size", val))
    fila.add_widget(etiqueta)
    caja = caja_de_texto(hint)
    fila.add_widget(caja)
    return fila, caja


class PantallaCultivos(ScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Este valor guarda el código del cultivo que se está editando.
        # Si es None, significa que NO estamos editando (estamos registrando uno nuevo).
        self.codigo_en_edicion = None

        contenido = BoxLayout(orientation="vertical", size_hint_y=None, padding=15, spacing=10)
        contenido.bind(minimum_height=contenido.setter("height"))
        self.add_widget(contenido)

        # --- Título ---
        titulo = Label(text="AgroSmart - Registro de Cultivos", font_size=24, bold=True,
                        size_hint_y=None, height=45, color=COLOR_VERDE_CLARO)
        contenido.add_widget(titulo)

        # --- Aviso de modo edición (solo se ve cuando se está editando algo) ---
        self.aviso_edicion = Label(text="", size_hint_y=None, height=25, font_size=14,
                                    color=COLOR_INFO, bold=True)
        contenido.add_widget(self.aviso_edicion)

        # --- Campos del formulario ---
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

        # --- Botones de Registrar/Guardar y Cancelar edición, en la misma fila ---
        fila_acciones_form = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)
        self.boton_registrar = boton_estilizado("Registrar cultivo")
        self.boton_registrar.bind(on_press=self.registrar_cultivo)
        fila_acciones_form.add_widget(self.boton_registrar)

        self.boton_cancelar_edicion = boton_estilizado("Cancelar edición", color_fondo=(0.5, 0.3, 0.3, 1))
        self.boton_cancelar_edicion.bind(on_press=self.cancelar_edicion)
        fila_acciones_form.add_widget(self.boton_cancelar_edicion)
        contenido.add_widget(fila_acciones_form)

        # --- Mensaje de aviso (errores o confirmaciones del formulario) ---
        self.mensaje = Label(text="", size_hint_y=None, height=30, color=COLOR_ERROR)
        contenido.add_widget(self.mensaje)

        # --- Sección: Buscar ---
        fila, self.campo_buscar_nombre = fila_con_etiqueta("Buscar (nombre, tipo o parcela):", "ej: maíz, parcela 8")
        contenido.add_widget(fila)

        fila_botones = BoxLayout(orientation="horizontal", size_hint_y=None, height=45, spacing=10)
        boton_buscar = boton_estilizado("Buscar cultivo")
        boton_buscar.bind(on_press=self.buscar_cultivo)
        fila_botones.add_widget(boton_buscar)

        boton_ordenar = boton_estilizado("Ordenar por fecha de siembra")
        boton_ordenar.bind(on_press=self.ordenar_cultivos)
        fila_botones.add_widget(boton_ordenar)
        contenido.add_widget(fila_botones)

        self.mensaje_busqueda = Label(text="", size_hint_y=None, height=30, color=COLOR_INFO)
        contenido.add_widget(self.mensaje_busqueda)

        # --- Ayuda visible sobre qué hacer con los resultados ---
        self.ayuda_resultados = Label(
            text="", size_hint_y=None, height=0, font_size=13,
            color=COLOR_TEXTO_CLARO, halign="left",
        )
        contenido.add_widget(self.ayuda_resultados)

        # --- Contenedor de resultados de búsqueda (botones dinámicos) ---
        self.resultados_busqueda = BoxLayout(orientation="vertical", size_hint_y=None, height=0, spacing=5)
        contenido.add_widget(self.resultados_busqueda)

        # --- Sección: Eliminar ---
        fila, self.campo_codigo_eliminar = fila_con_etiqueta("Código a eliminar:", "ej: CULT001")
        contenido.add_widget(fila)
        boton_eliminar = boton_estilizado("Eliminar cultivo", color_fondo=(0.55, 0.25, 0.22, 1))
        boton_eliminar.bind(on_press=self.eliminar_cultivo)
        contenido.add_widget(boton_eliminar)

        # --- Lista de todos los cultivos ---
        contenido.add_widget(Label(text="Cultivos registrados:", size_hint_y=None, height=30,
                                    font_size=16, color=COLOR_VERDE_CLARO, bold=True))
        self.lista_texto = Label(text="", size_hint_y=None, halign="left", valign="top",
                                  font_size=14, color=COLOR_TEXTO_CLARO)
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

        if self.codigo_en_edicion is not None:
            # --- MODO EDICIÓN: actualizamos el cultivo que ya existía ---
            cultivo_existente = gestor.buscar_por_codigo_hash(self.codigo_en_edicion)
            cultivo_existente.nombre = nombre
            cultivo_existente.tipo = tipo
            cultivo_existente.tipo_tierra = tierra
            cultivo_existente.localidad = localidad
            cultivo_existente.numero_parcela = parcela
            cultivo_existente.tamano_parcela = tamano
            cultivo_existente.fecha_siembra = fecha
            gestor.guardar_datos()

            self.mensaje.color = COLOR_EXITO
            self.mensaje.text = f"Cultivo {self.codigo_en_edicion} actualizado correctamente."
            self._salir_de_modo_edicion()
        else:
            # --- MODO NORMAL: registramos un cultivo nuevo ---
            nuevo_cultivo = Cultivo(
                codigo=gestor.generar_codigo(),
                nombre=nombre, tipo=tipo, tipo_tierra=tierra, localidad=localidad,
                numero_parcela=parcela, tamano_parcela=tamano, fecha_siembra=fecha,
            )
            gestor.agregar_cultivo(nuevo_cultivo)
            self.mensaje.color = COLOR_EXITO
            self.mensaje.text = f"Cultivo '{nombre}' registrado con código {nuevo_cultivo.codigo}"

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

    def _entrar_a_modo_edicion(self, cultivo):
        # Llena el formulario con los datos del cultivo seleccionado,
        # y cambia el botón para dejar claro que ahora se está EDITANDO.
        self.codigo_en_edicion = cultivo.codigo
        self.campo_nombre.text = cultivo.nombre
        self.campo_tipo.text = cultivo.tipo
        self.campo_tierra.text = cultivo.tipo_tierra
        self.campo_localidad.text = cultivo.localidad
        self.campo_parcela.text = str(cultivo.numero_parcela)
        self.campo_tamano.text = str(cultivo.tamano_parcela)
        self.campo_fecha.text = cultivo.fecha_siembra

        self.boton_registrar.text = "Guardar cambios"
        self.aviso_edicion.text = f" Editando el cultivo {cultivo.codigo} — modifica los campos y presiona 'Guardar cambios'."

    def _salir_de_modo_edicion(self):
        self.codigo_en_edicion = None
        self.boton_registrar.text = "Registrar cultivo"
        self.aviso_edicion.text = ""

    def cancelar_edicion(self, instancia_boton):
        # Si estaba editando, cancela y limpia el formulario sin guardar cambios
        self._salir_de_modo_edicion()
        self._limpiar_formulario()
        self.mensaje.color = COLOR_INFO
        self.mensaje.text = "Edición cancelada."

    def buscar_cultivo(self, instancia_boton):
        texto_buscado = self.campo_buscar_nombre.text.strip()

        self.resultados_busqueda.clear_widgets()
        self.resultados_busqueda.height = 0
        self.ayuda_resultados.text = ""
        self.ayuda_resultados.height = 0

        if not texto_buscado:
            self.mensaje_busqueda.color = COLOR_ERROR
            self.mensaje_busqueda.text = "Escribe algo para buscar (nombre, tipo o parcela)."
            return

        coincidencias = gestor.buscar_coincidencias(texto_buscado)

        if len(coincidencias) == 0:
            self.mensaje_busqueda.color = COLOR_ERROR
            self.mensaje_busqueda.text = "No se encontró ningún cultivo con eso."
            return

        self.mensaje_busqueda.color = COLOR_EXITO
        cantidad = len(coincidencias)
        palabra = "coincidencia" if cantidad == 1 else "coincidencias"
        self.mensaje_busqueda.text = f"{cantidad} {palabra} encontrada(s):"

        self.ayuda_resultados.text = "Toca un resultado para EDITARLO (también se copia su código abajo, por si prefieres eliminarlo):"
        self.ayuda_resultados.height = 20
        self.ayuda_resultados.text_size = (self.width - 30, None)

        for cultivo in coincidencias:
            boton_resultado = Button(
                text=str(cultivo),
                size_hint_y=None,
                height=40,
                halign="left",
                background_normal="",
                background_color=(0.18, 0.28, 0.2, 1),
                color=COLOR_TEXTO_CLARO,
            )
            boton_resultado.bind(size=lambda inst, val: setattr(inst, "text_size", val))
            boton_resultado.bind(on_press=lambda inst, cultivo=cultivo: self.mostrar_seleccionado(cultivo))
            self.resultados_busqueda.add_widget(boton_resultado)

        self.resultados_busqueda.height = cantidad * 45

    def mostrar_seleccionado(self, cultivo):
        # Al tocar un resultado: lo carga en el formulario para editar,
        # Y también copia su código a la caja de eliminar, por si se prefiere borrar.
        self._entrar_a_modo_edicion(cultivo)
        self.campo_codigo_eliminar.text = cultivo.codigo
        self.mensaje_busqueda.color = COLOR_INFO
        self.mensaje_busqueda.text = f"Cargado en el formulario para editar: {cultivo}"

    def ordenar_cultivos(self, instancia_boton):
        gestor.ordenar_por_fecha_siembra()
        self.mensaje_busqueda.color = COLOR_INFO
        self.mensaje_busqueda.text = "Cultivos ordenados por fecha de siembra."
        self.actualizar_lista()

    def eliminar_cultivo(self, instancia_boton):
        codigo_texto = self.campo_codigo_eliminar.text.strip()

        if not codigo_texto:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = "Escribe el código del cultivo a eliminar."
            return

        codigo_normalizado = self._normalizar_codigo(codigo_texto)
        cultivo_encontrado = gestor.buscar_por_codigo_hash(codigo_normalizado)

        if cultivo_encontrado is None:
            self.mensaje.color = COLOR_ERROR
            self.mensaje.text = f"No existe ningún cultivo con el código '{codigo_normalizado}'."
            return

        # Si el cultivo que se está editando es el mismo que se va a eliminar,
        # salimos del modo edición para no dejar el formulario en un estado raro.
        if self.codigo_en_edicion == codigo_normalizado:
            self._salir_de_modo_edicion()
            self._limpiar_formulario()

        gestor.eliminar_cultivo(codigo_normalizado)
        self.mensaje.color = COLOR_EXITO
        self.mensaje.text = f"Cultivo '{cultivo_encontrado.nombre}' ({codigo_normalizado}) eliminado."
        self.campo_codigo_eliminar.text = ""
        self.actualizar_lista()

    def _normalizar_codigo(self, texto):
        texto = texto.strip().upper()
        if texto.startswith("CULT"):
            texto = texto[4:]
        if texto.isdigit():
            return f"CULT{int(texto):03d}"
        return texto

    def actualizar_lista(self):
        if len(gestor.lista_cultivos) == 0:
            self.lista_texto.text = "No hay cultivos registrados todavía."
        else:
            lineas = [str(cultivo) for cultivo in gestor.lista_cultivos]
            self.lista_texto.text = "\n".join(lineas)


class AgroSmartApp(App):
    def build(self):
        self.title = "AgroSmart"
        return PantallaCultivos()


if __name__ == "__main__":
    AgroSmartApp().run()