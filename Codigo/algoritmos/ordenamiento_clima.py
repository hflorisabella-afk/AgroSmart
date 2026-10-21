# ordenamiento_clima.py
# Segundo algoritmo de ordenamiento - Merge Sort
# Ordena el pronostico de 5 dias por temperatura o probabilidad de lluvia


def merge_sort(lista_climas, clave="temperatura"):
    """
    Ordena una lista de objetos Clima usando Merge Sort (divide y venceras).

    Parametros:
        lista_climas (list): lista de objetos Clima (ej: el pronostico de 5 dias)
        clave (str): atributo por el cual ordenar -> "temperatura" o "probabilidad_lluvia"

    Retorna:
        list: nueva lista de objetos Clima ordenada de menor a mayor segun la clave
    """
    if len(lista_climas) <= 1:
        return lista_climas

    medio = len(lista_climas) // 2
    izquierda = merge_sort(lista_climas[:medio], clave)
    derecha = merge_sort(lista_climas[medio:], clave)

    return _combinar(izquierda, derecha, clave)


def _combinar(izquierda, derecha, clave):
    """Mezcla dos listas de objetos Clima ya ordenadas en una sola ordenada."""
    resultado = []
    i = j = 0

    while i < len(izquierda) and j < len(derecha):
        if getattr(izquierda[i], clave) <= getattr(derecha[j], clave):
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1

    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado