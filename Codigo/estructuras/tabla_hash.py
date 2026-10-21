# tabla_hash.py
# Implementación propia de una Tabla Hash (no usamos el diccionario de Python directo,
# para poder explicar bien cómo funciona por dentro en el documento técnico).
# Sirve para encontrar un cultivo a partir de su código de forma casi instantánea.
#
# --- ¿CÓMO FUNCIONA UNA TABLA HASH? ---
# Imagina un estante con muchos casilleros numerados (0, 1, 2, 3...).
# Cuando quieres guardar algo con una "llave" (ej. el código "CULT001"),
# una función matemática (la "función hash") convierte esa llave en un número,
# y ese número te dice en qué casillero guardar el dato.
# Así, para buscarlo después, no hay que revisar todos los casilleros:
# se vuelve a calcular el mismo número y se va DIRECTO a ese casillero.
#
# Puede pasar que dos llaves distintas caigan en el mismo casillero (esto se llama "colisión").
# Por eso cada casillero es en realidad una lista pequeña, donde caben varias llaves
# si llegan a coincidir.


class TablaHash:
    def __init__(self, tamano=50):
        # 'tamano' es la cantidad de casilleros que va a tener esta tabla.
        # Cada casillero empieza como una lista vacía (ahí es donde se guardan los datos).
        self.tamano = tamano
        self.casilleros = [[] for _ in range(tamano)]

    def _calcular_indice(self, llave):
        # --- FUNCIÓN HASH ---
        # Convierte la llave (ej. "CULT001") en un número de casillero.
        # Sumamos el valor numérico (ASCII) de cada letra de la llave,
        # y usamos el residuo (%) para que el número siempre caiga
        # dentro del rango de casilleros que existen.
        suma = sum(ord(caracter) for caracter in str(llave))
        return suma % self.tamano

    def insertar(self, llave, valor):
        # --- INSERTAR ---
        # Complejidad temporal: O(1) en el caso promedio (sin colisiones).
        # Complejidad espacial: O(n) por guardar todos los datos.
        indice = self._calcular_indice(llave)
        casillero = self.casilleros[indice]

        # Si la llave ya existía, actualizamos su valor en vez de duplicarla
        for posicion, (llave_guardada, _) in enumerate(casillero):
            if llave_guardada == llave:
                casillero[posicion] = (llave, valor)
                return

        # Si no existía, la agregamos como un par (llave, valor)
        casillero.append((llave, valor))

    def buscar(self, llave):

        # --- BUSCAR ---
        # Complejidad temporal: O(1) en el caso promedio -> calculamos el
        # casillero directo y solo revisamos ese (normalmente tiene 0 o 1 elementos).
        # En el peor caso (muchas colisiones en el mismo casillero), sería O(n).
        indice = self._calcular_indice(llave)
        casillero = self.casilleros[indice]

        for llave_guardada, valor in casillero:
            if llave_guardada == llave:
                return valor

        return None  # no se encontró

    def eliminar(self, llave):
        # --- ELIMINAR ---
        # Complejidad temporal: O(1) en el caso promedio.
        indice = self._calcular_indice(llave)
        casillero = self.casilleros[indice]

        for posicion, (llave_guardada, _) in enumerate(casillero):
            if llave_guardada == llave:
                casillero.pop(posicion)
                return True

        return False




# --- Zona de prueba ---
if __name__ == "__main__":
    tabla = TablaHash()

    tabla.insertar("CULT001", "Maíz parcela 3")
    tabla.insertar("CULT002", "Frijol parcela 1")

    print("Buscando CULT001:", tabla.buscar("CULT001"))
    print("Buscando CULT002:", tabla.buscar("CULT002"))
    print("Buscando CULT999 (no existe):", tabla.buscar("CULT999"))