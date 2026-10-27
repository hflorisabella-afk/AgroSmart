# unidades.py
# Conversión de unidades de terreno usadas en Guatemala.
# Por dentro la app guarda todo en HECTÁREAS; aquí solo se convierte
# para mostrarle al agricultor algo que entiende.
#
# Este archivo va en Codigo/modelos/ (junto a cultivo.py y gestor_cultivos.py).
#
# Ojo: el tamaño de la manzana y de la cuerda varía un poco según la región,
# así que estos valores son aproximados.

HA_POR_MANZANA = 0.6987
CUERDAS_POR_MANZANA = 16
HA_POR_CUERDA = HA_POR_MANZANA / CUERDAS_POR_MANZANA

UNIDADES = ["Manzanas", "Cuerdas", "Hectáreas"]


def a_hectareas(valor, unidad):
    # Pasa lo que escribió la persona a hectáreas
    valor = float(valor)

    if unidad == "Manzanas":
        return valor * HA_POR_MANZANA
    if unidad == "Cuerdas":
        return valor * HA_POR_CUERDA
    return valor


def de_hectareas(hectareas):
    # Devuelve (número, unidad) para mostrar en el formulario:
    # manzanas si es una manzana o más, cuerdas si es menos.
    ha = float(hectareas)
    manzanas = ha / HA_POR_MANZANA

    if manzanas >= 1:
        return round(manzanas, 2), "Manzanas"

    return round(ha / HA_POR_CUERDA, 1), "Cuerdas"


def texto_terreno(hectareas):
    # Texto corto para las tarjetas: "2.5 manzanas" o "5 cuerdas"
    try:
        ha = float(hectareas)
    except (TypeError, ValueError):
        return "tamaño desconocido"

    manzanas = ha / HA_POR_MANZANA

    if manzanas >= 1:
        n = round(manzanas, 1)
        return f"{n:g} manzana" + ("" if n == 1 else "s")

    cuerdas = max(1, round(ha / HA_POR_CUERDA))
    return f"{cuerdas} cuerda" + ("" if cuerdas == 1 else "s")