# lista_enlazada.py
# LISTA ENLAZADA: cada nodo guarda un dato y apunta al siguiente nodo.
# Agregar al inicio o al final es O(1) (guardamos un puntero al último).
# Recorrer la lista es O(n). Complejidad espacial: O(n).


class NodoLista:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    def __init__(self):
        self.cabeza = None
        self.ultimo = None
        self.cantidad = 0

    def agregar_al_inicio(self, dato):
        nuevo = NodoLista(dato)
        nuevo.siguiente = self.cabeza
        self.cabeza = nuevo
        if self.ultimo is None:
            self.ultimo = nuevo
        self.cantidad += 1

    def agregar_al_final(self, dato):
        nuevo = NodoLista(dato)
        if self.ultimo is None:
            self.cabeza = nuevo
            self.ultimo = nuevo
        else:
            self.ultimo.siguiente = nuevo
            self.ultimo = nuevo
        self.cantidad += 1

    def a_lista(self):
        # Recorre nodo por nodo y devuelve una lista normal de Python. O(n)
        resultado = []
        actual = self.cabeza
        while actual is not None:
            resultado.append(actual.dato)
            actual = actual.siguiente
        return resultado

    def __len__(self):
        return self.cantidad


# --- Zona de prueba ---
if __name__ == "__main__":
    lista = ListaEnlazada()
    lista.agregar_al_inicio("primero")
    lista.agregar_al_inicio("segundo (queda arriba)")
    lista.agregar_al_final("ultimo")
    print(lista.a_lista(), "-> total:", len(lista))