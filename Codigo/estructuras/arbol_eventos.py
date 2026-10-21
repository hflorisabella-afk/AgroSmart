# arbol_eventos.py
# Árbol Binario de Búsqueda (BST) para guardar los eventos del calendario
# ordenados por fecha.
#
# Regla del árbol: en cada nodo, los eventos con fecha MENOR van a la izquierda
# y los de fecha IGUAL o MAYOR van a la derecha.
# Si recorremos el árbol "en orden" (izquierda -> nodo -> derecha),
# los eventos salen ordenados por fecha automáticamente.
#
# Complejidad temporal de insertar y buscar: O(log n) en el caso promedio,
# O(n) en el peor caso (si los datos llegan ya ordenados y el árbol queda "estirado").
# Complejidad del recorrido en orden: O(n).
# Complejidad espacial: O(n), un nodo por cada evento.


class NodoArbol:
    def __init__(self, evento):
        self.evento = evento
        self.izquierdo = None
        self.derecho = None


class ArbolEventos:
    def __init__(self):
        self.raiz = None
        self.cantidad = 0

    def insertar(self, evento):
        nuevo = NodoArbol(evento)
        self.cantidad += 1

        if self.raiz is None:
            self.raiz = nuevo
            return

        actual = self.raiz
        while True:
            if evento.fecha < actual.evento.fecha:
                if actual.izquierdo is None:
                    actual.izquierdo = nuevo
                    return
                actual = actual.izquierdo
            else:
                if actual.derecho is None:
                    actual.derecho = nuevo
                    return
                actual = actual.derecho

    def en_orden(self):
        # Devuelve la lista de eventos ordenados por fecha (recorrido en orden)
        resultado = []
        pila = []
        actual = self.raiz

        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izquierdo
            actual = pila.pop()
            resultado.append(actual.evento)
            actual = actual.derecho

        return resultado

    def buscar_por_fecha(self, fecha):
        # Devuelve todos los eventos que ocurren en esa fecha
        encontrados = []
        actual = self.raiz

        while actual is not None:
            if fecha < actual.evento.fecha:
                actual = actual.izquierdo
            else:
                if fecha == actual.evento.fecha:
                    encontrados.append(actual.evento)
                actual = actual.derecho

        return encontrados


# --- Zona de prueba ---
if __name__ == "__main__":
    class EventoPrueba:
        def __init__(self, fecha):
            self.fecha = fecha

    arbol = ArbolEventos()
    for f in ["2026-10-08", "2026-09-15", "2026-09-20", "2026-09-15"]:
        arbol.insertar(EventoPrueba(f))

    print("En orden:", [e.fecha for e in arbol.en_orden()])
    print("Buscar 2026-09-15:", len(arbol.buscar_por_fecha("2026-09-15")), "evento(s)")