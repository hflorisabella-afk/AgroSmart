# gestor_cultivos.py
# Este archivo se encarga de administrar TODOS los cultivos juntos:
# agregar nuevos, ver la lista completa, buscar, y ahora también
# GUARDAR y CARGAR los datos en un archivo, para que no se pierdan al cerrar el programa.
# cultivo.py define "qué es un cultivo", este archivo dice "qué hacer con varios cultivos".

import json  # nos sirve para guardar y leer datos en un archivo de texto ordenado
import os
import sys

# Esta línea le dice a Python "también busca archivos dentro de la carpeta estructuras",
# que está un nivel arriba (Codigo/) y luego adentro de estructuras/.
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "estructuras"))

from cultivo import Cultivo
from tabla_hash import TablaHash

# Este es el nombre del archivo donde se van a guardar todos los cultivos.
# Se va a crear automáticamente junto a este mismo archivo (dentro de modelos/).
ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "datos_cultivos.json")


class GestorCultivos:
    def __init__(self):
        self.lista_cultivos = []
        self.contador = 0
        # --- TABLA HASH ---
        # Un diccionario en Python es, por dentro, una Tabla Hash.
        # La usamos para encontrar un cultivo por su código de forma INSTANTÁNEA,
        # sin tener que recorrer toda la lista como en la búsqueda lineal.
        # La "llave" es el código (ej. "CULT001") y el "valor" es el objeto Cultivo completo.
        self.tabla_hash_codigos = TablaHash()
        self.cargar_datos()

    def generar_codigo(self):
        self.contador += 1
        return f"CULT{self.contador:03d}"

    def agregar_cultivo(self, cultivo):
        self.lista_cultivos.append(cultivo)
        # Cada vez que se agrega un cultivo, también lo guardamos en la tabla hash
        self.tabla_hash_codigos.insertar(cultivo.codigo, cultivo)
        print(f"Cultivo agregado: {cultivo.nombre} (código: {cultivo.codigo})")
        self.guardar_datos()

    def eliminar_cultivo(self, codigo_a_eliminar):
        # Busca el cultivo por su código (usando la tabla hash, que es instantáneo)
        cultivo_encontrado = self.tabla_hash_codigos.buscar(codigo_a_eliminar)

        if cultivo_encontrado is None:
            return False  # no existe ese código, no hay nada que eliminar

        # Lo quitamos de la lista principal
        self.lista_cultivos.remove(cultivo_encontrado)
        # También lo quitamos de la tabla hash, insertando un valor vacío en su lugar
        self.tabla_hash_codigos.insertar(codigo_a_eliminar, None)
        self.guardar_datos()
        return True  # se eliminó correctamente

    def mostrar_todos(self):
        if len(self.lista_cultivos) == 0:
            print("No hay cultivos registrados todavía.")
            return

        print("--- Lista de cultivos ---")
        for cultivo in self.lista_cultivos:
            print(cultivo)

    def buscar_por_nombre(self, nombre_buscado):
        # --- BÚSQUEDA LINEAL ---
        # Esto es un algoritmo de búsqueda: revisa la lista UNO POR UNO
        # hasta encontrar un cultivo cuyo nombre coincida (o hasta terminar la lista).
        # Complejidad: O(n) -> en el peor caso revisa TODOS los cultivos.
        for cultivo in self.lista_cultivos:
            if cultivo.nombre.lower() == nombre_buscado.lower():
                return cultivo
        return None

    def buscar_coincidencias(self, texto_buscado):
        # Busca TODOS los cultivos donde el texto aparezca en el nombre, el tipo
        # o la localidad (no necesita ser exacto, ej. "parcela 8" o "maíz" encuentran
        # cualquier cultivo que tenga esas palabras en alguno de esos campos).
        # A diferencia de buscar_por_nombre, esta función devuelve una LISTA
        # con todas las coincidencias, no solo una.
        texto_buscado = texto_buscado.lower().strip()
        resultados = []

        for cultivo in self.lista_cultivos:
            if (texto_buscado in cultivo.nombre.lower()
                    or texto_buscado in cultivo.tipo.lower()
                    or texto_buscado in cultivo.localidad.lower()
                    or texto_buscado in str(cultivo.numero_parcela).lower()):
                resultados.append(cultivo)

        return resultados

    def buscar_por_codigo_hash(self, codigo_buscado):
        # --- BÚSQUEDA POR TABLA HASH ---
        # A diferencia de la búsqueda lineal, aquí NO recorremos nada:
        # el diccionario calcula directamente en qué "casillero" está guardado
        # el cultivo según su código, y lo entrega de inmediato.
        # Complejidad temporal: O(1) en el caso promedio -> no importa si hay 10 o 10,000 cultivos.
        # Complejidad espacial: O(n) -> porque guardamos una copia de cada cultivo en el diccionario.
        return self.tabla_hash_codigos.buscar(codigo_buscado)
        # .buscar() devuelve None automáticamente si el código no existe, sin dar error

    def buscar_por_nombre_binaria(self, nombre_buscado):
        # --- BÚSQUEDA BINARIA ---
        # Este algoritmo es mucho más rápido que la lineal, PERO necesita
        # que la lista ya esté ordenada alfabéticamente por nombre para funcionar.
        # La idea: en vez de revisar uno por uno, cada vez "parte a la mitad" el
        # espacio de búsqueda, descartando la mitad donde el nombre NO puede estar.
        #
        # Complejidad temporal: O(log n) -> muchísimo más rápido que O(n) en listas grandes.
        # Complejidad espacial: O(n) -> por la copia ordenada que creamos para no
        # desordenar la lista original (que puede estar ordenada por fecha, no por nombre).

        # Hacemos una copia ordenada por nombre, sin tocar el orden original de la lista
        lista_ordenada = sorted(self.lista_cultivos, key=lambda c: c.nombre.lower())

        nombre_buscado = nombre_buscado.lower()
        inicio = 0
        fin = len(lista_ordenada) - 1

        while inicio <= fin:
            medio = (inicio + fin) // 2  # el punto exacto de la mitad
            nombre_medio = lista_ordenada[medio].nombre.lower()

            if nombre_medio == nombre_buscado:
                return lista_ordenada[medio]  # lo encontramos
            elif nombre_medio < nombre_buscado:
                inicio = medio + 1  # el que buscamos está en la mitad de la derecha
            else:
                fin = medio - 1  # el que buscamos está en la mitad de la izquierda

        return None  # si inicio pasa a fin, es que no existe

    def ordenar_por_fecha_siembra(self):
        # --- ORDENAMIENTO POR INSERCIÓN (Insertion Sort) ---
        # La idea es parecida a cómo ordenas cartas en la mano:
        # tomas una carta y la vas metiendo en el lugar correcto entre las que ya tenías ordenadas.
        #
        # Recorremos la lista desde el segundo elemento en adelante.
        # Cada cultivo lo comparamos con los que están ANTES de él (ya ordenados),
        # y lo vamos "empujando" hacia atrás hasta encontrar su lugar correcto por fecha.
        #
        # Complejidad temporal: O(n²) en el peor caso (lista al revés),
        # porque por cada elemento puede que tengamos que compararlo con todos los anteriores.
        # Complejidad espacial: O(1), porque ordenamos "en el mismo lugar",
        # sin crear una lista nueva ni usar memoria extra.

        for i in range(1, len(self.lista_cultivos)):
            actual = self.lista_cultivos[i]
            j = i - 1

            # Mientras el de atrás exista y su fecha sea MAYOR que la del actual,
            # lo corremos un puesto a la derecha (le hacemos espacio)
            while j >= 0 and self.lista_cultivos[j].fecha_siembra > actual.fecha_siembra:
                self.lista_cultivos[j + 1] = self.lista_cultivos[j]
                j -= 1

            # Aquí ya encontramos el lugar correcto para "actual"
            self.lista_cultivos[j + 1] = actual

        # Guardamos el nuevo orden en el archivo, para que quede reflejado también ahí
        self.guardar_datos()

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
            self.tabla_hash_codigos.insertar(cultivo.codigo, cultivo)  # también lo agregamos a la tabla hash

        # El contador se calcula según el NÚMERO más alto que ya se haya usado,
        # no según cuántos cultivos hay ahora. Esto evita que se repita un código
        # si alguna vez se elimina un cultivo (ej. si se borra CULT002 y solo queda
        # CULT001, el próximo código debe ser CULT003, no CULT002 de nuevo).
        numero_mas_alto = 0
        for cultivo in self.lista_cultivos:
            numero = int(cultivo.codigo.replace("CULT", ""))
            if numero > numero_mas_alto:
                numero_mas_alto = numero
        self.contador = numero_mas_alto


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