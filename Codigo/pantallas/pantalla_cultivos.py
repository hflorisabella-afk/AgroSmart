# pantalla_cultivos.py
# Esta es la primera pantalla visual de AgroSmart.
# Permite registrar un cultivo nuevo y ver la lista de cultivos ya registrados.
# Toda la lógica "de fondo" (guardar, validar, etc.) ya la hicimos antes en
# modelos/cultivo.py y modelos/gestor_cultivos.py — aquí solo conectamos
# esa lógica con botones y cajas de texto en pantalla.

import sys
import os
from datetime import datetime

# Le decimos a Python dónde buscar los archivos de la carpeta "modelos",
# que está un nivel arriba (Codigo/) y luego adentro de modelos/.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modelos"))

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos

from kivy.app import App
from kivy.core.window import Window

# Agrandamos la ventana para que quepa todo el formulario sin encimarse
Window.size = (750, 750)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView

# Un solo gestor para toda la app, igual que hicimos en principal.py
gestor = GestorCultivos()


class PantallaCultivos(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 15
        self.spacing = 10

        # --- Título ---
        titulo = Label(
            text="AgroSmart - Registro de Cultivos",
            font_size=22,
            size_hint=(1, 0.08),
            bold=True,
        )
        self.add_widget(titulo)

        # --- Formulario: una cajita de texto por cada dato del cultivo ---
        formulario = GridLayout(cols=2, size_hint=(1, 0.5), spacing=12)

        formulario.add_widget(Label(text="Nombre del cultivo:", font_size=16))
        self.campo_nombre = TextInput(multiline=False, hint_text="ej: Maíz parcela 5", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_nombre)

        formulario.add_widget(Label(text="Tipo de cultivo:", font_size=16))
        self.campo_tipo = TextInput(multiline=False, hint_text="ej: Maíz, Frijol, Café", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_tipo)

        formulario.add_widget(Label(text="Tipo de tierra:", font_size=16))
        self.campo_tierra = TextInput(multiline=False, hint_text="ej: Arcillosa, Arenosa", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_tierra)

        formulario.add_widget(Label(text="Localidad:", font_size=16))
        self.campo_localidad = TextInput(multiline=False, hint_text="ej: Chimaltenango", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_localidad)

        formulario.add_widget(Label(text="Número de parcela:", font_size=16))
        self.campo_parcela = TextInput(multiline=False, hint_text="ej: 3", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_parcela)

        formulario.add_widget(Label(text="Tamaño de parcela (ha):", font_size=16))
        self.campo_tamano = TextInput(multiline=False, hint_text="ej: 2.5", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_tamano)

        formulario.add_widget(Label(text="Fecha de siembra (AAAA-MM-DD):", font_size=16))
        self.campo_fecha = TextInput(multiline=False, hint_text="ej: 2026-08-19", font_size=18, padding=[12, 12, 12, 12])
        formulario.add_widget(self.campo_fecha)

        self.add_widget(formulario)

        # --- Botón para registrar ---
        boton_registrar = Button(text="Registrar cultivo", size_hint=(1, 0.08))
        boton_registrar.bind(on_press=self.registrar_cultivo)
        self.add_widget(boton_registrar)

        # --- Mensaje de aviso (errores o confirmaciones) ---
        self.mensaje = Label(text="", size_hint=(1, 0.06), color=(1, 0.4, 0.4, 1))
        self.add_widget(self.mensaje)

        # --- Sección para eliminar un cultivo ---
        fila_eliminar = BoxLayout(orientation="horizontal", size_hint=(1, 0.08), spacing=8)
        fila_eliminar.add_widget(Label(text="Código a eliminar:", size_hint=(0.4, 1)))
        self.campo_codigo_eliminar = TextInput(multiline=False, hint_text="ej: CULT001", size_hint=(0.35, 1), font_size=18, padding=[12, 12, 12, 12])
        fila_eliminar.add_widget(self.campo_codigo_eliminar)
        boton_eliminar = Button(text="Eliminar cultivo", size_hint=(0.25, 1))
        boton_eliminar.bind(on_press=self.eliminar_cultivo)
        fila_eliminar.add_widget(boton_eliminar)
        self.add_widget(fila_eliminar)

        # --- Lista de cultivos ya registrados, con scroll ---
        self.add_widget(Label(text="Cultivos registrados:", size_hint=(1, 0.05)))
        scroll = ScrollView(size_hint=(1, 0.3))
        self.lista_texto = Label(text="", size_hint_y=None, valign="top", halign="left")
        self.lista_texto.bind(texture_size=self._actualizar_altura_lista)
        scroll.add_widget(self.lista_texto)
        self.add_widget(scroll)

        # Mostramos lo que ya estaba guardado desde antes (si había)
        self.actualizar_lista()

    def _actualizar_altura_lista(self, instancia, tamano):
        # Esto hace que el texto de la lista pueda crecer y el scroll funcione bien
        instancia.height = tamano[1]
        instancia.text_size = (instancia.width, None)

    def registrar_cultivo(self, instancia_boton):
        # --- Validaciones, igual que hicimos en principal.py ---
        nombre = self.campo_nombre.text.strip()
        tipo = self.campo_tipo.text.strip()
        tierra = self.campo_tierra.text.strip()
        localidad = self.campo_localidad.text.strip()
        parcela = self.campo_parcela.text.strip()
        tamano_texto = self.campo_tamano.text.strip()
        fecha = self.campo_fecha.text.strip()

        # Campos obligatorios: ninguno puede quedar vacío
        if not nombre or not tipo or not tierra or not localidad or not parcela:
            self.mensaje.text = "Todos los campos son obligatorios."
            return

        # El tamaño debe ser un número mayor a 0
        try:
            tamano = float(tamano_texto)
            if tamano <= 0:
                self.mensaje.text = "El tamaño debe ser mayor a 0."
                return
        except ValueError:
            self.mensaje.text = "El tamaño debe ser un número, ej. 2.5."
            return

        # La fecha debe tener el formato correcto
        try:
            datetime.strptime(fecha, "%Y-%m-%d")
        except ValueError:
            self.mensaje.text = "Fecha inválida. Usa el formato AAAA-MM-DD."
            return

        # Si todo está bien, creamos el cultivo y lo guardamos
        nuevo_cultivo = Cultivo(
            codigo=gestor.generar_codigo(),
            nombre=nombre,
            tipo=tipo,
            tipo_tierra=tierra,
            localidad=localidad,
            numero_parcela=parcela,
            tamano_parcela=tamano,
            fecha_siembra=fecha,
        )
        gestor.agregar_cultivo(nuevo_cultivo)

        self.mensaje.color = (0.4, 1, 0.4, 1)
        self.mensaje.text = f"Cultivo '{nombre}' registrado con código {nuevo_cultivo.codigo}"

        # Limpiamos el formulario para el siguiente registro
        self.campo_nombre.text = ""
        self.campo_tipo.text = ""
        self.campo_tierra.text = ""
        self.campo_localidad.text = ""
        self.campo_parcela.text = ""
        self.campo_tamano.text = ""
        self.campo_fecha.text = ""

        self.actualizar_lista()

    def eliminar_cultivo(self, instancia_boton):
        codigo_texto = self.campo_codigo_eliminar.text.strip()

        if not codigo_texto:
            self.mensaje.color = (1, 0.4, 0.4, 1)
            self.mensaje.text = "Escribe el código del cultivo a eliminar."
            return

        # Aceptamos "CULT001", "cult1" o solo "1", igual que en el menú de texto
        codigo_normalizado = self._normalizar_codigo(codigo_texto)
        cultivo_encontrado = gestor.buscar_por_codigo_hash(codigo_normalizado)

        if cultivo_encontrado is None:
            self.mensaje.color = (1, 0.4, 0.4, 1)
            self.mensaje.text = f"No existe ningún cultivo con el código '{codigo_normalizado}'."
            return

        gestor.eliminar_cultivo(codigo_normalizado)
        self.mensaje.color = (0.4, 1, 0.4, 1)
        self.mensaje.text = f"Cultivo '{cultivo_encontrado.nombre}' ({codigo_normalizado}) eliminado."
        self.campo_codigo_eliminar.text = ""
        self.actualizar_lista()

    def _normalizar_codigo(self, texto):
        # Misma lógica que usamos en principal.py: acepta CULT001, cult1, 001 o 1
        texto = texto.strip().upper()
        if texto.startswith("CULT"):
            texto = texto[4:]
        if texto.isdigit():
            return f"CULT{int(texto):03d}"
        return texto

    def actualizar_lista(self):
        # Vuelve a armar el texto de la lista completa de cultivos
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