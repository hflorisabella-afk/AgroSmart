# grafo.py
# GRAFO no dirigido con pesos, hecho con lista de adyacencia:
# cada nodo guarda un diccionario con sus vecinos y la distancia a cada uno.
# En AgroSmart: los nodos son el TANQUE y las parcelas, y las aristas son canales (en metros).
# Complejidad espacial: O(V + E).


class Grafo:
    def __init__(self):
        self.adyacencia = {}

    def agregar_nodo(self, nodo):
        if nodo not in self.adyacencia:
            self.adyacencia[nodo] = {}

    def agregar_arista(self, a, b, peso):
        # Une dos nodos con un canal de 'peso' metros (en los dos sentidos). O(1)
        self.agregar_nodo(a)
        self.agregar_nodo(b)
        self.adyacencia[a][b] = peso
        self.adyacencia[b][a] = peso

    def vecinos(self, nodo):
        return list(self.adyacencia.get(nodo, {}).items())

    def nodos(self):
        return list(self.adyacencia.keys())

    def existe(self, nodo):
        return nodo in self.adyacencia


# --- Zona de prueba ---
if __name__ == "__main__":
    g = Grafo()
    g.agregar_arista("TANQUE", "CULT001", 100)
    g.agregar_arista("CULT001", "CULT002", 50)
    print(g.nodos())
    print(g.vecinos("CULT001"))