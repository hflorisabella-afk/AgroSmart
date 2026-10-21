# voraz_agua.py
# ALGORITMO VORAZ (greedy): reparto de agua limitada entre varios cultivos.
#
# Idea: a cada cultivo le calculamos su "ratio" = valor / necesidad
# (cuánta importancia da cada litro). Ordenamos de mayor a menor ratio con
# Merge Sort y vamos dando agua en ese orden hasta que se acabe.
# El último cultivo puede recibir agua parcial (como en la mochila fraccionaria).
#
# Complejidad temporal: O(n log n), por el Merge Sort (el reparto es O(n)).
# Complejidad espacial: O(n), por las listas del Merge Sort.

from ordenamiento_clima import merge_sort


class ItemAgua:
    def __init__(self, codigo, nombre, necesidad, prioridad, valor):
        self.codigo = codigo
        self.nombre = nombre
        self.necesidad = necesidad      # litros que necesita
        self.prioridad = prioridad      # 1 a 10
        self.valor = valor              # importancia total del cultivo
        self.ratio = valor / necesidad if necesidad > 0 else 0
        self.asignado = 0.0             # litros que recibe

    def porcentaje(self):
        if self.necesidad <= 0:
            return 0
        return 100 * self.asignado / self.necesidad


def repartir_agua(items, agua_total):
    # Devuelve (items ordenados por ratio de mayor a menor, litros sobrantes)
    ordenados = merge_sort(items, clave="ratio")[::-1]
    restante = agua_total

    for item in ordenados:
        if restante <= 0:
            item.asignado = 0.0
            continue
        entregado = min(item.necesidad, restante)
        item.asignado = entregado
        restante -= entregado

    return ordenados, restante


# --- Zona de prueba ---
if __name__ == "__main__":
    items = [
        ItemAgua("CULT001", "maiz", 2000, 6, 12),
        ItemAgua("CULT002", "frijol", 1500, 10, 15),
        ItemAgua("CULT003", "sandia", 3000, 3, 9),
    ]
    resultado, sobra = repartir_agua(items, 4000)
    for it in resultado:
        print(it.codigo, "recibe", it.asignado, "de", it.necesidad)
    print("Sobra:", sobra)