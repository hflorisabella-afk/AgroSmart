# cola.py
# COLA (Queue): el primero que entra es el primero que sale (FIFO).
# Está hecha con nodos enlazados, así que meter y sacar es siempre O(1).
# Complejidad espacial: O(n).


class NodoCola:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class Cola:
    def __init__(self):
        self.frente = None   # el próximo en salir
        self.final = None    # el último que entró
        self._cantidad = 0

    def encolar(self, dato):
        # Agrega al final de la fila. O(1)
        nuevo = NodoCola(dato)
        if self.final is None:
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self._cantidad += 1

    def desencolar(self):
        # Saca al que está al frente. O(1)
        if self.frente is None:
            return None
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self._cantidad -= 1
        return dato

    def esta_vacia(self):
        return self.frente is None

    def cantidad(self):
        return self._cantidad

    def a_lista(self):
        # Devuelve los datos en orden de salida (sin sacarlos). O(n)
        resultado = []
        actual = self.frente
        while actual is not None:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado


# --- Zona de prueba ---
if __name__ == "__main__":
    cola = Cola()
    cola.encolar("CULT001")
    cola.encolar("CULT002")
    cola.encolar("CULT003")
    print("En espera:", cola.a_lista())
    print("Sale:", cola.desencolar())
    print("En espera:", cola.a_lista())