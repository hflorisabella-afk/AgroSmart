# dijkstra.py
# ALGORITMO DE GRAFOS: Dijkstra (camino más corto con pesos positivos).
# En AgroSmart: la ruta de canales más corta desde el TANQUE hasta una parcela.
#
# Idea: siempre sacamos el nodo con la menor distancia conocida, y revisamos
# si pasando por él llegamos más rápido a sus vecinos.
#
# Complejidad temporal: O((V + E) log V), usando una cola de prioridad (heapq).
# Complejidad espacial: O(V), por las distancias y los nodos anteriores.

import heapq


def dijkstra(grafo, origen):
    distancias = {nodo: float("inf") for nodo in grafo.nodos()}
    anterior = {}
    distancias[origen] = 0
    pendientes = [(0, origen)]

    while pendientes:
        distancia_actual, nodo = heapq.heappop(pendientes)

        if distancia_actual > distancias[nodo]:
            continue  # ya encontramos un camino mejor antes

        for vecino, peso in grafo.vecinos(nodo):
            nueva = distancia_actual + peso
            if nueva < distancias[vecino]:
                distancias[vecino] = nueva
                anterior[vecino] = nodo
                heapq.heappush(pendientes, (nueva, vecino))

    return distancias, anterior


def ruta_mas_corta(grafo, origen, destino):
    # Devuelve (distancia_total, [nodos del camino]) o (None, []) si no hay camino.
    if not grafo.existe(origen) or not grafo.existe(destino):
        return None, []

    distancias, anterior = dijkstra(grafo, origen)

    if distancias[destino] == float("inf"):
        return None, []

    camino = [destino]
    while camino[-1] != origen:
        camino.append(anterior[camino[-1]])
    camino.reverse()

    return distancias[destino], camino


# --- Zona de prueba ---
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "estructuras"))
    from grafo import Grafo

    g = Grafo()
    g.agregar_arista("TANQUE", "A", 100)
    g.agregar_arista("A", "B", 50)
    g.agregar_arista("TANQUE", "B", 200)

    print(ruta_mas_corta(g, "TANQUE", "B"))  # esperado: (150, ['TANQUE', 'A', 'B'])