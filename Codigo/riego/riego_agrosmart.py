# riego_agrosmart.py
# Lógica del módulo de Riego de AgroSmart.
# Los cultivos NO se registran aquí.
# Se obtienen desde GestorCultivos para mantener un solo registro de cultivos.

import json
import os
import random
from dataclasses import dataclass
from datetime import datetime, date
from abc import ABC, abstractmethod

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "modelos"))

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROBABILIDAD_LLUVIA_POSTERGA = 0.60
MM_LLUVIA_POSTERGA = 3.0

CAUDAL_LITROS_POR_MINUTO_HA = 10
DURACION_MAXIMA_MINUTOS = 30
HUMEDAD_INICIAL = 45.0


# Configuración de humedad según tipo de tierra
PERFILES_SUELO = {
    "arcillosa": {
        "min": 25,
        "objetivo": 50
    },
    "arenosa": {
        "min": 35,
        "objetivo": 55
    },
    "franca": {
        "min": 30,
        "objetivo": 55
    },
    "limosa": {
        "min": 28,
        "objetivo": 52
    }
}


# Ajustes según tipo de cultivo
AJUSTES_CULTIVO = {
    "maíz": 0,
    "maiz": 0,
    "frijol": -5,
    "café": 5,
    "cafe": 5,
    "tomate": 5,
    "papa": 0,
    "arroz": 10,
    "hortalizas": 5
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def normalizar_codigo(codigo):
    """
    Convierte códigos como:
    CULT001
    cult1
    001
    1

    en:
    CULT001
    """

    codigo = str(codigo).strip().upper()

    if codigo.startswith("CULT"):
        codigo = codigo[4:]

    if codigo.isdigit():
        return f"CULT{int(codigo):03d}"

    return codigo


def calcular_etapa_crecimiento(fecha_siembra):
    """
    Calcula la etapa del cultivo según los días desde la siembra.
    """

    try:
        fecha = datetime.strptime(fecha_siembra, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return "creciendo", 0

    dias = (date.today() - fecha).days

    if dias <= 15:
        return "recién sembrado", 10

    elif dias <= 60:
        return "creciendo", 0

    else:
        return "maduro", -5


def calcular_configuracion_zona(cultivo):
    """
    Calcula la configuración de riego usando los datos
    que vienen del registro principal de Cultivos.
    """

    tierra = cultivo.tipo_tierra.lower().strip()

    perfil = PERFILES_SUELO.get(
        tierra,
        {
            "min": 30,
            "objetivo": 55
        }
    )

    humedad_minima = perfil["min"]
    humedad_objetivo = perfil["objetivo"]

    tipo_cultivo = cultivo.tipo.lower().strip()

    ajuste_cultivo = 0

    for nombre, ajuste in AJUSTES_CULTIVO.items():
        if nombre in tipo_cultivo:
            ajuste_cultivo = ajuste
            break

    etapa, ajuste_etapa = calcular_etapa_crecimiento(
        cultivo.fecha_siembra
    )

    humedad_minima += ajuste_cultivo
    humedad_objetivo += ajuste_cultivo

    humedad_minima += ajuste_etapa
    humedad_objetivo += ajuste_etapa

    # Evitamos valores fuera de un rango razonable
    humedad_minima = max(10, min(humedad_minima, 80))
    humedad_objetivo = max(humedad_minima + 5, min(humedad_objetivo, 90))

    return ConfiguracionZona(
        nombre=cultivo.nombre,
        humedad_minima=humedad_minima,
        humedad_objetivo=humedad_objetivo,
        duracion_maxima=DURACION_MAXIMA_MINUTOS,
        caudal=CAUDAL_LITROS_POR_MINUTO_HA,
        etapa=etapa
    )


# ============================================================
# CONFIGURACIÓN DE ZONA
# ============================================================

@dataclass
class ConfiguracionZona:
    nombre: str
    humedad_minima: float
    humedad_objetivo: float
    duracion_maxima: int
    caudal: float
    etapa: str


# ============================================================
# SENSOR DE HUMEDAD
# ============================================================

class SensorHumedad:

    def __init__(self, humedad_inicial=HUMEDAD_INICIAL):
        self.humedad = float(humedad_inicial)

    def leer(self):
        """
        Simula una pequeña variación natural de humedad.
        """

        perdida = random.uniform(0, 2)

        self.humedad -= perdida

        if self.humedad < 0:
            self.humedad = 0

        return round(self.humedad, 2)

    def registrar_riego(self, minutos, litros_por_minuto):
        """
        Aumenta la humedad después de realizar el riego.
        """

        aumento = minutos * litros_por_minuto * 0.05

        self.humedad += aumento

        if self.humedad > 100:
            self.humedad = 100

        return round(self.humedad, 2)


# ============================================================
# VÁLVULA
# ============================================================

class Valvula:

    def __init__(self):
        self.abierta = False

    def abrir(self):
        self.abierta = True

    def cerrar(self):
        self.abierta = False


# ============================================================
# REGISTRO DE RIEGO
# ============================================================

@dataclass
class RegistroRiego:
    fecha_hora: str
    litros_estimados: float
    motivo: str


# ============================================================
# ZONA DE RIEGO
# ============================================================

class ZonaRiego:

    def __init__(
        self,
        cultivo,
        humedad_inicial=HUMEDAD_INICIAL,
        historial=None
    ):
        self.cultivo = cultivo

        self.sensor = SensorHumedad(humedad_inicial)

        self.valvula = Valvula()

        self.configuracion = calcular_configuracion_zona(
            cultivo
        )

        self.historial = historial if historial else []

    def recalcular_configuracion(self):
        self.configuracion = calcular_configuracion_zona(
            self.cultivo
        )

    def necesita_riego(self, humedad=None):

        if humedad is None:
            humedad = self.sensor.leer()

        return humedad < self.configuracion.humedad_minima


# ============================================================
# CLIMA PARA RIEGO
# ============================================================

@dataclass
class PronosticoClima:
    probabilidad_lluvia: float
    milimetros_lluvia: float


class ProveedorClima(ABC):

    @abstractmethod
    def obtener_pronostico(self, localidad):
        pass


class ProveedorClimaSimulado(ProveedorClima):

    def obtener_pronostico(self, localidad):

        return PronosticoClima(
            probabilidad_lluvia=random.uniform(0, 1),
            milimetros_lluvia=random.uniform(0, 10)
        )


class ProveedorClimaFijo(ProveedorClima):

    def __init__(
        self,
        probabilidad_lluvia,
        milimetros_lluvia
    ):
        self.probabilidad_lluvia = probabilidad_lluvia
        self.milimetros_lluvia = milimetros_lluvia

    def obtener_pronostico(self, localidad):

        return PronosticoClima(
            self.probabilidad_lluvia,
            self.milimetros_lluvia
        )


PROVEEDOR_CLIMA = ProveedorClimaSimulado()


# ============================================================
# PERSISTENCIA DEL MÓDULO DE RIEGO
# ============================================================

ARCHIVO_RIEGO = os.path.join(
    os.path.dirname(__file__),
    "datos_riego.json"
)


def cargar_datos_riego():

    if not os.path.exists(ARCHIVO_RIEGO):
        return {}

    try:
        with open(
            ARCHIVO_RIEGO,
            "r",
            encoding="utf-8"
        ) as archivo:

            return json.load(archivo)

    except (json.JSONDecodeError, OSError):

        return {}


def guardar_datos_riego(datos):

    with open(
        ARCHIVO_RIEGO,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            datos,
            archivo,
            ensure_ascii=False,
            indent=2
        )


# ============================================================
# GESTOR DE RIEGO
# ============================================================

class GestorRiego:

    def __init__(self, gestor_cultivos=None):

        self.gestor_cultivos = (
            gestor_cultivos
            if gestor_cultivos
            else GestorCultivos()
        )

        self.cultivos = {}
        self.zonas = {}

        self._cargar()

        self.sincronizar_con_cultivos()

    # --------------------------------------------------------
    # SINCRONIZACIÓN CON GESTOR CULTIVOS
    # --------------------------------------------------------

    def sincronizar_con_cultivos(self):

        cultivos_actuales = self.gestor_cultivos.lista_cultivos

        codigos_actuales = set()

        for cultivo in cultivos_actuales:

            codigo = cultivo.codigo

            codigos_actuales.add(codigo)

            self.cultivos[codigo] = cultivo

            if codigo not in self.zonas:

                datos_guardados = (
                    self.datos_guardados.get(
                        codigo,
                        {}
                    )
                )

                humedad = datos_guardados.get(
                    "humedad",
                    HUMEDAD_INICIAL
                )

                historial_datos = datos_guardados.get(
                    "historial",
                    []
                )

                historial = []

                for registro in historial_datos:

                    historial.append(
                        RegistroRiego(
                            fecha_hora=registro.get(
                                "fecha_hora",
                                ""
                            ),
                            litros_estimados=float(
                                registro.get(
                                    "litros_estimados",
                                    0
                                )
                            ),
                            motivo=registro.get(
                                "motivo",
                                ""
                            )
                        )
                    )

                self.zonas[codigo] = ZonaRiego(
                    cultivo,
                    humedad_inicial=humedad,
                    historial=historial
                )

            else:

                # Actualiza la referencia al cultivo principal
                self.zonas[codigo].cultivo = cultivo

                # Recalcula por si el usuario editó
                # tipo de tierra, tipo de cultivo o fecha.
                self.zonas[codigo].recalcular_configuracion()

        # Si un cultivo fue eliminado desde Cultivos,
        # también desaparece de las zonas activas de Riego.
        codigos_zonas = list(self.zonas.keys())

        for codigo in codigos_zonas:

            if codigo not in codigos_actuales:

                del self.zonas[codigo]

                if codigo in self.cultivos:
                    del self.cultivos[codigo]

        self.guardar()

    # --------------------------------------------------------
    # PERSISTENCIA
    # --------------------------------------------------------

    def _cargar(self):

        self.datos_guardados = cargar_datos_riego()

    def guardar(self):

        datos = {}

        for codigo, zona in self.zonas.items():

            datos[codigo] = {
                "humedad": zona.sensor.humedad,
                "historial": [
                    {
                        "fecha_hora": registro.fecha_hora,
                        "litros_estimados": registro.litros_estimados,
                        "motivo": registro.motivo
                    }
                    for registro in zona.historial
                ]
            }

        guardar_datos_riego(datos)

    # --------------------------------------------------------
    # BUSCAR CULTIVO
    # --------------------------------------------------------

    def buscar_por_codigo(self, codigo):

        codigo = normalizar_codigo(codigo)

        self.sincronizar_con_cultivos()

        return self.cultivos.get(codigo)

    # --------------------------------------------------------
    # OBTENER ZONA
    # --------------------------------------------------------

    def obtener_zona(self, codigo):

        codigo = normalizar_codigo(codigo)

        self.sincronizar_con_cultivos()

        return self.zonas.get(codigo)

    # --------------------------------------------------------
    # ELIMINAR
    # --------------------------------------------------------

    def eliminar_cultivo(self, codigo):

        codigo = normalizar_codigo(codigo)

        if codigo in self.zonas:

            del self.zonas[codigo]

        if codigo in self.cultivos:

            del self.cultivos[codigo]

        self.guardar()

    # --------------------------------------------------------
    # RECALCULAR CONFIGURACIONES
    # --------------------------------------------------------

    def recalcular_configuraciones(self):

        self.sincronizar_con_cultivos()

        for zona in self.zonas.values():

            zona.recalcular_configuracion()

        self.guardar()


# ============================================================
# CONTROLADOR DE RIEGO
# ============================================================

class ControladorRiego:

    def __init__(
        self,
        gestor_riego,
        proveedor_clima=None
    ):

        self.gestor_riego = gestor_riego

        self.proveedor_clima = (
            proveedor_clima
            if proveedor_clima
            else PROVEEDOR_CLIMA
        )

    # --------------------------------------------------------
    # REVISAR TODOS
    # --------------------------------------------------------

    def revisar_y_regar_todas(self):

        self.gestor_riego.sincronizar_con_cultivos()

        resultados = []

        if not self.gestor_riego.zonas:

            return resultados

        for zona in self.gestor_riego.zonas.values():

            resultado = self._revisar_zona(zona)

            resultados.append(resultado)

        self.gestor_riego.guardar()

        return resultados

    # --------------------------------------------------------
    # REVISAR UNA ZONA
    # --------------------------------------------------------

    def revisar_zona(self, codigo):

        zona = self.gestor_riego.obtener_zona(codigo)

        if zona is None:

            return {
                "codigo": normalizar_codigo(codigo),
                "estado": "error",
                "mensaje": "Cultivo no encontrado."
            }

        return self._revisar_zona(zona)

    # --------------------------------------------------------
    # LÓGICA PRINCIPAL
    # --------------------------------------------------------

    def _revisar_zona(self, zona):

        cultivo = zona.cultivo

        humedad_actual = zona.sensor.leer()

        pronostico = self.proveedor_clima.obtener_pronostico(
            cultivo.localidad
        )

        # ----------------------------------------------------
        # REVISIÓN DE LLUVIA
        # ----------------------------------------------------

        if (
            pronostico.probabilidad_lluvia
            >= PROBABILIDAD_LLUVIA_POSTERGA
            and
            pronostico.milimetros_lluvia
            >= MM_LLUVIA_POSTERGA
        ):

            return {
                "codigo": cultivo.codigo,
                "nombre": cultivo.nombre,
                "humedad": humedad_actual,
                "estado": "lluvia",
                "mensaje": (
                    "Se pospone el riego porque "
                    "se espera lluvia."
                ),
                "probabilidad_lluvia": round(
                    pronostico.probabilidad_lluvia * 100,
                    1
                ),
                "milimetros_lluvia": round(
                    pronostico.milimetros_lluvia,
                    1
                )
            }

        # ----------------------------------------------------
        # NO NECESITA RIEGO
        # ----------------------------------------------------

        if not zona.necesita_riego(humedad_actual):

            return {
                "codigo": cultivo.codigo,
                "nombre": cultivo.nombre,
                "humedad": humedad_actual,
                "estado": "correcto",
                "mensaje": (
                    "La humedad es suficiente. "
                    "No necesita riego."
                ),
                "probabilidad_lluvia": round(
                    pronostico.probabilidad_lluvia * 100,
                    1
                ),
                "milimetros_lluvia": round(
                    pronostico.milimetros_lluvia,
                    1
                )
            }

        # ----------------------------------------------------
        # CALCULAR RIEGO
        # ----------------------------------------------------

        humedad_objetivo = zona.configuracion.humedad_objetivo

        diferencia = humedad_objetivo - humedad_actual

        if diferencia <= 0:

            return {
                "codigo": cultivo.codigo,
                "nombre": cultivo.nombre,
                "humedad": humedad_actual,
                "estado": "correcto",
                "mensaje": "No necesita riego."
            }

        # Factor de reducción si existe posibilidad
        # moderada de lluvia.
        factor_lluvia = 1.0

        if pronostico.probabilidad_lluvia >= 0.30:

            factor_lluvia = 0.70

        # Cantidad de agua aproximada
        litros_por_ha = (
            diferencia * 2 * factor_lluvia
        )

        litros_totales = (
            litros_por_ha
            * cultivo.tamano_parcela
        )

        caudal_total = (
            zona.configuracion.caudal
            * cultivo.tamano_parcela
        )

        if caudal_total <= 0:

            caudal_total = 1

        minutos = litros_totales / caudal_total

        minutos = max(1, minutos)

        minutos = min(
            minutos,
            zona.configuracion.duracion_maxima
        )

        litros_estimados = (
            caudal_total * minutos
        )

        # ----------------------------------------------------
        # REALIZAR RIEGO
        # ----------------------------------------------------

        zona.valvula.abrir()

        humedad_despues = zona.sensor.registrar_riego(
            minutos,
            zona.configuracion.caudal
        )

        zona.valvula.cerrar()

        registro = RegistroRiego(
            fecha_hora=datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            litros_estimados=round(
                litros_estimados,
                2
            ),
            motivo=(
                "Humedad por debajo del mínimo."
            )
        )

        zona.historial.append(registro)

        self.gestor_riego.guardar()

        return {
            "codigo": cultivo.codigo,
            "nombre": cultivo.nombre,
            "humedad": humedad_actual,
            "humedad_despues": humedad_despues,
            "estado": "regado",
            "mensaje": (
                "Riego simulado realizado correctamente. "
            ),
            "minutos": round(minutos, 1),
            "litros": round(litros_estimados, 1),
            "probabilidad_lluvia": round(
                pronostico.probabilidad_lluvia * 100,
                1
            ),
            "milimetros_lluvia": round(
                pronostico.milimetros_lluvia,
                1
            )
        }