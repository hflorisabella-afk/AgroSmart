# planificador.py
# Junta las estructuras (cola, lista enlazada, grafo) y los algoritmos
# (Dijkstra y voraz) para la pantalla "Optimizar".
# También calcula la recomendación de agua de cada cultivo.
# Guarda todo en datos_optimizacion.json (junto a este archivo).

import json
import os
import sys
import unicodedata
from datetime import datetime, date

CARPETA = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CARPETA, "..", "estructuras"))
sys.path.append(os.path.join(CARPETA, "..", "algoritmos"))
sys.path.append(os.path.join(CARPETA, "..", "modelos"))

from unidades import texto_terreno  # se reexporta: la pantalla lo importa de aquí
from cola import Cola
from lista_enlazada import ListaEnlazada
from grafo import Grafo
from dijkstra import dijkstra, ruta_mas_corta
from voraz_agua import ItemAgua, repartir_agua as algoritmo_voraz

ARCHIVO = os.path.join(CARPETA, "datos_optimizacion.json")

# Punto de partida del recorrido (la casa del agricultor)
PUNTO_INICIO = "CASA"


# ============================================================
# TABLAS DE REFERENCIA (VALORES APROXIMADOS)
# Cambia estos números si consigues datos más exactos.
# Recuerda: 1 milímetro de agua sobre 1 hectárea = 10,000 litros.
# ============================================================

LITROS_POR_MM_HECTAREA = 10000

# Milímetros de agua por riego, según el tipo de cultivo
MM_POR_RIEGO = {
    "maiz": 25,
    "frijol": 20,
    "tomate": 25,
    "cafe": 15,
    "papa": 25,
    "arroz": 50,
    "hortalizas": 15,
    "sandia": 25,
}
MM_DEFECTO = 20

# Cada cuántos días se riega, según el tipo de cultivo
DIAS_ENTRE_RIEGOS = {
    "maiz": 8,
    "frijol": 8,
    "tomate": 4,
    "cafe": 15,
    "papa": 6,
    "arroz": 3,
    "hortalizas": 3,
    "sandia": 6,
}
DIAS_DEFECTO = 7

# La tierra arenosa se seca rápido (más agua y más seguido);
# la arcillosa retiene el agua (menos agua y más espaciado).
FACTOR_TIERRA = {
    "arenosa": 1.25,
    "arcillosa": 0.85,
    "franca": 1.0,
    "limosa": 0.9,
}
AJUSTE_DIAS_TIERRA = {
    "arenosa": -2,
    "arcillosa": 2,
    "franca": 0,
    "limosa": 1,
}

TEXTO_ETAPA = {
    "futuro": "Todavía no se siembra",
    "nueva": "Recién sembrado (necesita agua seguido)",
    "creciendo": "Creciendo",
    "madura": "Ya está grande (aguanta más sequía)",
    "desconocida": "No se pudo saber (revisa la fecha de siembra)",
}


def _limpiar(texto):
    # Pasa a minúsculas y quita tildes: "Maíz " -> "maiz"
    texto = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def calcular_etapa(fecha_siembra):
    # Devuelve (etapa, prioridad). La prioridad (1 a 10) dice qué tan
    # urgente es el agua: un cultivo recién sembrado es el más delicado.
    try:
        siembra = datetime.strptime(str(fecha_siembra), "%Y-%m-%d")
    except ValueError:
        return "desconocida", 5

    dias = (datetime.now() - siembra).days

    if dias < 0:
        return "futuro", 1
    if dias <= 15:
        return "nueva", 10
    if dias <= 60:
        return "creciendo", 6
    return "madura", 3


class Planificador:
    def __init__(self):
        self.cola = Cola()                  # riegos pendientes (el primero en llegar es el primero en regarse)
        self.historial = ListaEnlazada()    # riegos ya hechos (el más nuevo primero)
        self.grafo = Grafo()                # distancias entre la casa y las parcelas
        self.grafo.agregar_nodo(PUNTO_INICIO)
        self.canales = []                   # lista de {"desde", "hasta", "km"}
        self.cargar()

    # ---------------- guardar y cargar ----------------

    def cargar(self):
        if not os.path.exists(ARCHIVO):
            return
        try:
            with open(ARCHIVO, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except (OSError, json.JSONDecodeError):
            return

        for codigo in datos.get("cola", []):
            self.cola.encolar(codigo)
        for registro in datos.get("historial", []):
            self.historial.agregar_al_final(registro)
        for canal in datos.get("canales", []):
            try:
                desde = PUNTO_INICIO if canal["desde"] == "TANQUE" else canal["desde"]
                hasta = PUNTO_INICIO if canal["hasta"] == "TANQUE" else canal["hasta"]
                self._poner_canal(desde, hasta, float(canal["km"]))
            except (KeyError, ValueError):
                pass

    def guardar(self):
        datos = {
            "cola": self.cola.a_lista(),
            "historial": self.historial.a_lista(),
            "canales": self.canales,
        }
        try:
            with open(ARCHIVO, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
        except OSError:
            print("No se pudo guardar datos_optimizacion.json")

    # ---------------- recomendación de agua ----------------

    def recomendar(self, cultivo):
        tipo = _limpiar(cultivo.tipo)
        tierra = _limpiar(cultivo.tipo_tierra)

        try:
            tamano = float(cultivo.tamano_parcela)
        except (TypeError, ValueError):
            tamano = 1.0

        mm = MM_POR_RIEGO.get(tipo, MM_DEFECTO)
        litros = tamano * mm * LITROS_POR_MM_HECTAREA * FACTOR_TIERRA.get(tierra, 1.0)
        litros = max(100, round(litros, -2))

        dias = DIAS_ENTRE_RIEGOS.get(tipo, DIAS_DEFECTO) + AJUSTE_DIAS_TIERRA.get(tierra, 0)
        dias = max(2, dias)

        etapa, prioridad = calcular_etapa(cultivo.fecha_siembra)

        return {
            "litros": litros,
            "dias": dias,
            "etapa": etapa,
            "etapa_texto": TEXTO_ETAPA[etapa],
            "prioridad": prioridad,
        }

    def necesidad_total(self, cultivos):
        total = 0
        for c in cultivos:
            rec = self.recomendar(c)
            if rec["etapa"] != "futuro":
                total += rec["litros"]
        return total

    # ---------------- cola e historial ----------------

    def en_cola(self, codigo):
        return codigo in self.cola.a_lista()

    def programar_riego(self, codigo):
        # Devuelve False si ya estaba en la lista de pendientes
        if self.en_cola(codigo):
            return False
        self.cola.encolar(codigo)
        self.guardar()
        return True

    def atender_siguiente(self):
        codigo = self.cola.desencolar()
        if codigo is None:
            return None
        registro = {
            "codigo": codigo,
            "momento": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.historial.agregar_al_inicio(registro)
        self.guardar()
        return registro

    def ultimo_riego(self, codigo):
        # El historial guarda primero el más nuevo, así que el primero que
        # coincida es el último riego de ese cultivo.
        for registro in self.historial.a_lista():
            if registro.get("codigo") == codigo:
                try:
                    return datetime.strptime(registro["momento"][:10], "%Y-%m-%d").date()
                except (ValueError, KeyError):
                    return None
        return None

    def estado_riego(self, cultivo, rec):
        # Devuelve (texto, clave). Claves: "urgente", "bien", "pendiente", "info"
        if rec["etapa"] == "futuro":
            return "Todavía no se siembra: aún no necesita riego.", "info"

        if self.en_cola(cultivo.codigo):
            return "Ya está en la lista de pendientes por regar.", "pendiente"

        ultimo = self.ultimo_riego(cultivo.codigo)

        if ultimo is None:
            return "Todavía no hay ningún riego anotado. ¡Toca regar!", "urgente"

        dias = (date.today() - ultimo).days

        if dias >= rec["dias"]:
            return f"Último riego hace {dias} día(s). ¡Toca regar!", "urgente"

        faltan = rec["dias"] - dias

        if dias == 0:
            return f"Se regó hoy. Próximo riego en {faltan} día(s).", "bien"

        return f"Último riego hace {dias} día(s). Próximo riego en {faltan} día(s).", "bien"

    # ---------------- distancias entre lugares (grafo) ----------------

    def _poner_canal(self, desde, hasta, km):
        # Si ya existía una distancia entre esos dos puntos, se reemplaza
        self.canales = [
            c for c in self.canales
            if {c["desde"], c["hasta"]} != {desde, hasta}
        ]
        self.canales.append({"desde": desde, "hasta": hasta, "km": km})
        self.grafo.agregar_arista(desde, hasta, km)

    def agregar_canal(self, desde, hasta, km):
        self._poner_canal(desde, hasta, km)
        self.guardar()

    def borrar_canales(self):
        self.canales = []
        self.grafo = Grafo()
        self.grafo.agregar_nodo(PUNTO_INICIO)
        self.guardar()

    def ruta_mas_corta(self, destino):
        return ruta_mas_corta(self.grafo, PUNTO_INICIO, destino)

    def orden_de_visita(self, codigos):
        # Algoritmo voraz: desde donde estás, ve siempre a la parcela
        # pendiente más cercana. Devuelve (orden, km_totales, sin_camino).
        actual = PUNTO_INICIO
        faltan = list(codigos)
        orden = []
        total = 0

        while faltan and self.grafo.existe(actual):
            distancias, _ = dijkstra(self.grafo, actual)
            alcanzables = [
                c for c in faltan
                if self.grafo.existe(c) and distancias[c] != float("inf")
            ]
            if not alcanzables:
                break
            siguiente = min(alcanzables, key=lambda c: distancias[c])
            total += distancias[siguiente]
            orden.append(siguiente)
            faltan.remove(siguiente)
            actual = siguiente

        return orden, total, faltan

    # ---------------- reparto de agua (algoritmo voraz) ----------------

    def repartir_agua(self, cultivos, litros):
        items = []

        for c in cultivos:
            rec = self.recomendar(c)

            if rec["etapa"] == "futuro":
                continue  # lo que aún no se siembra no necesita agua

            try:
                tamano = float(c.tamano_parcela)
            except (TypeError, ValueError):
                tamano = 1.0

            valor = rec["prioridad"] * tamano
            items.append(ItemAgua(c.codigo, c.nombre, rec["litros"], rec["prioridad"], valor))

        if not items:
            return [], litros

        return algoritmo_voraz(items, litros)