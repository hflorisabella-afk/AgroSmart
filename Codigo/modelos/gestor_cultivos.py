# gestor_cultivos.py
# Este archivo se encarga de administrar TODOS los cultivos juntos:
# agregar nuevos, ver la lista completa, buscar, y ahora también
# GUARDAR y CARGAR los datos en un archivo, para que no se pierdan al cerrar el programa.
# cultivo.py define "qué es un cultivo", este archivo dice "qué hacer con varios cultivos".

import json  # nos sirve para guardar y leer datos en un archivo de texto ordenado
import os
from cultivo import Cultivo

# Este es el nombre del archivo donde se van a guardar todos los cultivos.
# Se va a crear automáticamente junto a este mismo archivo (dentro de modelos/).
ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "datos_cultivos.json")


class GestorCultivos:
    def __init__(self):
        self.lista_cultivos = []
        self.contador = 0
        self.cargar_datos()

    def generar_codigo(self):
        self.contador += 1
        return f"CULT{self.contador:03d}"

    def agregar_cultivo(self, cultivo):
        self.lista_cultivos.append(cultivo)
        print(f"Cultivo agregado: {cultivo.nombre} (código: {cultivo.codigo})")
        self.guardar_datos()

    def mostrar_todos(self):
        if len(self.lista_cultivos) == 0:
            print("No hay cultivos registrados todavía.")
            return

        print("--- Lista de cultivos ---")
        for cultivo in self.lista_cultivos:
            print(cultivo)

    def buscar_por_nombre(self, nombre_buscado):
        for cultivo in self.lista_cultivos:
            if cultivo.nombre.lower() == nombre_buscado.lower():
                return cultivo
        return None

    def guardar_datos(self):
        lista_como_diccionarios = [cultivo.__dict__ for cultivo in self.lista_cultivos]
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as archivo:
            json.dump(lista_como_diccionarios, archivo, ensure_ascii=False, indent=2)

    def cargar_datos(self):
        if not os.path.exists(ARCHIVO_DATOS):
            return

        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as archivo:
            lista_como_diccionarios = json.load(archivo)

        for datos in lista_como_diccionarios:
            cultivo = Cultivo(
                codigo=datos["codigo"],
                nombre=datos["nombre"],
                tipo=datos["tipo"],
                tipo_tierra=datos["tipo_tierra"],
                localidad=datos["localidad"],
                numero_parcela=datos["numero_parcela"],
                tamano_parcela=datos["tamano_parcela"],
                fecha_siembra=datos["fecha_siembra"],
                estado=datos["estado"]
            )
            self.lista_cultivos.append(cultivo)

        self.contador = len(self.lista_cultivos)


# --- Zona de prueba ---
if __name__ == "__main__":
    gestor = GestorCultivos()

    print(f"Cultivos ya cargados desde el archivo: {len(gestor.lista_cultivos)}")
    gestor.mostrar_todos()

    print("\nBuscando 'Frijol parcela 1'...")
    resultado = gestor.buscar_por_nombre("Frijol parcela 1")
    if resultado:
        print(f"¡Encontrado! {resultado}")
    else:
        print("No se encontró ese cultivo.")