"""
Sistema de Riego Inteligente — PROGRAMA INDEPENDIENTE, UN SOLO ARCHIVO.

Este programa NO depende de ningún otro sistema. Registra sus propios
cultivos (código, nombre, tipo, tipo de tierra, localidad, número de
parcela, tamaño de parcela y fecha de siembra) y, a partir de esos datos,
calcula un control de riego eficiente y personalizado para cada cultivo.

Cómo decide cuánto y cuándo regar cada cultivo (combina TODOS los datos):
  - tipo_tierra    -> qué tan rápido pierde humedad el suelo
                       (arcillosa retiene más, arenosa drena más rápido)
  - tipo (cultivo) -> cuánta agua necesita ese cultivo en particular
  - tamano_parcela -> escala el caudal de riego (litros/minuto)
  - fecha_siembra  -> calcula automáticamente la etapa de crecimiento
                       (recién sembrado / creciendo / maduro) y ajusta
                       qué tan seguido debe regarse

Uso:
    python riego_agrosmart.py
"""

from __future__ import annotations

import json
import os
import random
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional


# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

RUTA_DATOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_riego.json")

# --- Umbrales de decisión climática ---
UMBRAL_PROBABILIDAD_LLUVIA = 0.6   # 0-1, si se supera junto con el umbral de mm, se pospone el riego
UMBRAL_MM_LLUVIA_ESPERADA = 3.0

# --- Perfiles según tipo de tierra (qué tan rápido pierde humedad el suelo) ---
PERFILES_TIPO_TIERRA = {
    "arcillosa": {"humedad_minima": 25.0, "humedad_objetivo": 50.0},
    "arenosa":   {"humedad_minima": 35.0, "humedad_objetivo": 55.0},
    "franca":    {"humedad_minima": 30.0, "humedad_objetivo": 55.0},
    "limosa":    {"humedad_minima": 28.0, "humedad_objetivo": 52.0},
}
PERFIL_TIERRA_DEFECTO = {"humedad_minima": 30.0, "humedad_objetivo": 55.0}

# --- Ajuste según tipo de cultivo (cuánta agua necesita cada uno) ---
# Valor positivo = necesita más humedad disponible; negativo = tolera más sequía.
AJUSTE_POR_TIPO_CULTIVO = {
    "maíz": 0.0,
    "maiz": 0.0,
    "frijol": -5.0,
    "café": 5.0,
    "cafe": 5.0,
    "tomate": 5.0,
    "papa": 0.0,
    "arroz": 10.0,
    "hortalizas": 5.0,
}
AJUSTE_TIPO_CULTIVO_DEFECTO = 0.0

# --- Ajuste según etapa de crecimiento (calculada desde fecha_siembra) ---
DIAS_ETAPA_RECIEN_SEMBRADO = 15   # 0-15 días: necesita humedad constante
DIAS_ETAPA_CRECIENDO = 60         # 16-60 días: etapa normal
# más de 60 días: se considera "maduro", tolera algo más de sequía

AJUSTE_RECIEN_SEMBRADO = 10.0
AJUSTE_CRECIENDO = 0.0
AJUSTE_MADURO = -5.0

# --- Escalado según tamaño de parcela ---
CAUDAL_LITROS_MIN_POR_HECTAREA = 10.0
DURACION_MAXIMA_RIEGO_MIN = 30

HUMEDAD_INICIAL_POR_DEFECTO = 45.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("riego_agrosmart")


# ============================================================
# MODELOS DE DOMINIO
# ============================================================

@dataclass
class ConfiguracionZona:
    """Configuración de riego calculada para un cultivo en particular."""
    nombre: str
    humedad_minima: float
    humedad_objetivo: float
    duracion_maxima_riego_min: int
    caudal_litros_min: float
    etapa_crecimiento: str


class SensorHumedad:
    """Sensor de humedad del suelo (simulado, con persistencia)."""

    def __init__(self, humedad_inicial: float, simulado: bool = True):
        self._humedad = humedad_inicial
        self.simulado = simulado
        self._ultima_lectura = datetime.now()

    def leer(self) -> float:
        if self.simulado:
            self._simular_evaporacion()
        return round(self._humedad, 1)

    def _simular_evaporacion(self) -> None:
        ahora = datetime.now()
        minutos_transcurridos = (ahora - self._ultima_lectura).total_seconds() / 60
        perdida = minutos_transcurridos * 0.05 + random.uniform(0, 0.3)
        self._humedad = max(0.0, self._humedad - perdida)
        self._ultima_lectura = ahora

    def registrar_riego(self, incremento: float) -> None:
        self._humedad = min(100.0, self._humedad + incremento)


class Valvula:
    """Representa la válvula/actuador físico de una zona de riego."""

    def __init__(self, nombre: str, simulado: bool = True):
        self.nombre = nombre
        self.simulado = simulado
        self.abierta = False

    def abrir(self) -> None:
        self.abierta = True
        if self.simulado:
            print(f"  [VÁLVULA] '{self.nombre}' ABIERTA (simulado)")
        # Para hardware real: GPIO.output(self.pin, GPIO.HIGH)

    def cerrar(self) -> None:
        self.abierta = False
        if self.simulado:
            print(f"  [VÁLVULA] '{self.nombre}' CERRADA (simulado)")
        # Para hardware real: GPIO.output(self.pin, GPIO.LOW)


@dataclass
class RegistroRiego:
    momento: str
    litros_estimados: float
    motivo: str


@dataclass
class Cultivo:
    """Representa un cultivo registrado, con todos sus datos."""
    codigo: str
    nombre: str
    tipo: str
    tipo_tierra: str
    localidad: str
    numero_parcela: str
    tamano_parcela: float
    fecha_siembra: str

    def __str__(self) -> str:
        return (f"[{self.codigo}] {self.nombre} ({self.tipo}) - {self.localidad}, "
                f"parcela {self.numero_parcela} ({self.tamano_parcela} ha) - "
                f"sembrado el {self.fecha_siembra}")


class ZonaRiego:
    """Une un cultivo con su sensor, válvula y configuración de riego calculada."""

    def __init__(self, cultivo: Cultivo, config: ConfiguracionZona,
                 sensor: SensorHumedad, valvula: Valvula):
        self.cultivo = cultivo
        self.config = config
        self.sensor = sensor
        self.valvula = valvula
        self.historial: list[RegistroRiego] = []

    def necesita_riego(self) -> bool:
        return self.sensor.leer() < self.config.humedad_minima

    def __str__(self) -> str:
        return (f"[{self.cultivo.codigo}] {self.cultivo.nombre} - etapa: {self.config.etapa_crecimiento} - "
                f"humedad actual: {self.sensor.leer()}% (mínimo: {self.config.humedad_minima}%, "
                f"objetivo: {self.config.humedad_objetivo}%)")


# ============================================================
# CLIMA (interfaz lista para conectar tu sistema real más adelante)
# ============================================================

@dataclass
class PronosticoClima:
    probabilidad_lluvia: float   # 0.0 a 1.0
    mm_lluvia_esperada: float
    temperatura_c: float
    viento_kmh: float = 0.0


class ProveedorClima(ABC):
    """
    Interfaz para cualquier fuente de datos climáticos.

    Cuando conectes tu sistema de clima real, crea una clase que herede de
    ProveedorClima e implemente obtener_pronostico(). Luego reemplaza la
    variable PROVEEDOR_CLIMA más abajo en este archivo. Nada más cambia.
    """

    @abstractmethod
    def obtener_pronostico(self) -> PronosticoClima:
        raise NotImplementedError


class ProveedorClimaSimulado(ProveedorClima):
    """Proveedor de clima simulado, mientras no haya un sistema de clima real conectado."""

    def obtener_pronostico(self) -> PronosticoClima:
        return PronosticoClima(
            probabilidad_lluvia=round(random.uniform(0, 1), 2),
            mm_lluvia_esperada=round(random.uniform(0, 10), 1),
            temperatura_c=round(random.uniform(15, 32), 1),
            viento_kmh=round(random.uniform(0, 20), 1),
        )


class ProveedorClimaFijo(ProveedorClima):
    """Proveedor de clima con valores fijos, útil para pruebas deterministas."""

    def __init__(self, pronostico: PronosticoClima):
        self._pronostico = pronostico

    def obtener_pronostico(self) -> PronosticoClima:
        return self._pronostico


PROVEEDOR_CLIMA: ProveedorClima = ProveedorClimaSimulado()


# ============================================================
# PERSISTENCIA (un solo archivo propio: datos_riego.json)
# ============================================================

def cargar_datos() -> dict:
    if not os.path.exists(RUTA_DATOS):
        return {"cultivos": {}}
    with open(RUTA_DATOS, "r", encoding="utf-8") as archivo:
        return json.load(archivo)


def guardar_datos(datos: dict) -> None:
    with open(RUTA_DATOS, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


# ============================================================
# LÓGICA DE CÁLCULO DE RIEGO (combina todos los aspectos del cultivo)
# ============================================================

def calcular_etapa_crecimiento(fecha_siembra: str) -> str:
    """Calcula la etapa de crecimiento según los días transcurridos desde la siembra."""
    try:
        fecha = datetime.strptime(fecha_siembra, "%Y-%m-%d")
    except ValueError:
        return "desconocida"

    dias = (datetime.now() - fecha).days

    if dias < 0:
        return "no sembrado aún"
    elif dias <= DIAS_ETAPA_RECIEN_SEMBRADO:
        return "recién sembrado"
    elif dias <= DIAS_ETAPA_CRECIENDO:
        return "creciendo"
    else:
        return "maduro"


def _ajuste_por_etapa(etapa: str) -> float:
    return {
        "recién sembrado": AJUSTE_RECIEN_SEMBRADO,
        "creciendo": AJUSTE_CRECIENDO,
        "maduro": AJUSTE_MADURO,
    }.get(etapa, 0.0)


def calcular_configuracion_zona(cultivo: Cultivo) -> ConfiguracionZona:
    """
    Calcula los umbrales de riego para un cultivo combinando:
    tipo de tierra, tipo de cultivo, tamaño de parcela y etapa de crecimiento.
    """
    tipo_tierra = cultivo.tipo_tierra.strip().lower()
    perfil_tierra = PERFILES_TIPO_TIERRA.get(tipo_tierra, PERFIL_TIERRA_DEFECTO)

    ajuste_cultivo = AJUSTE_POR_TIPO_CULTIVO.get(cultivo.tipo.strip().lower(), AJUSTE_TIPO_CULTIVO_DEFECTO)

    etapa = calcular_etapa_crecimiento(cultivo.fecha_siembra)
    ajuste_etapa = _ajuste_por_etapa(etapa)

    humedad_minima = perfil_tierra["humedad_minima"] + ajuste_cultivo + ajuste_etapa
    humedad_objetivo = perfil_tierra["humedad_objetivo"] + ajuste_cultivo

    # Mantenemos los valores dentro de un rango razonable (0-95%)
    humedad_minima = max(5.0, min(95.0, humedad_minima))
    humedad_objetivo = max(humedad_minima + 5.0, min(95.0, humedad_objetivo))

    caudal = round(CAUDAL_LITROS_MIN_POR_HECTAREA * max(cultivo.tamano_parcela, 0.1), 1)

    return ConfiguracionZona(
        nombre=cultivo.nombre,
        humedad_minima=round(humedad_minima, 1),
        humedad_objetivo=round(humedad_objetivo, 1),
        duracion_maxima_riego_min=DURACION_MAXIMA_RIEGO_MIN,
        caudal_litros_min=caudal,
        etapa_crecimiento=etapa,
    )


# ============================================================
# GESTOR: registra cultivos y arma sus zonas de riego
# ============================================================

class GestorRiego:
    def __init__(self):
        self.cultivos: Dict[str, Cultivo] = {}
        self.zonas: Dict[str, ZonaRiego] = {}
        self.contador = 0
        self._cargar()

    def _cargar(self) -> None:
        datos = cargar_datos()
        for codigo, info in datos.get("cultivos", {}).items():
            cultivo = Cultivo(
                codigo=codigo,
                nombre=info["nombre"],
                tipo=info["tipo"],
                tipo_tierra=info["tipo_tierra"],
                localidad=info["localidad"],
                numero_parcela=info["numero_parcela"],
                tamano_parcela=info["tamano_parcela"],
                fecha_siembra=info["fecha_siembra"],
            )
            self.cultivos[codigo] = cultivo

            config_zona = calcular_configuracion_zona(cultivo)
            sensor = SensorHumedad(humedad_inicial=info.get("humedad", HUMEDAD_INICIAL_POR_DEFECTO))
            valvula = Valvula(nombre=f"{codigo}-{cultivo.nombre}")
            zona = ZonaRiego(cultivo=cultivo, config=config_zona, sensor=sensor, valvula=valvula)

            for evento in info.get("historial", []):
                zona.historial.append(RegistroRiego(**evento))

            self.zonas[codigo] = zona

        # El contador se basa en el número más alto ya usado, para no repetir códigos
        numero_mas_alto = 0
        for codigo in self.cultivos:
            if codigo.startswith("CULT") and codigo[4:].isdigit():
                numero_mas_alto = max(numero_mas_alto, int(codigo[4:]))
        self.contador = numero_mas_alto

    def guardar(self) -> None:
        datos = {"cultivos": {}}
        for codigo, zona in self.zonas.items():
            cultivo = zona.cultivo
            datos["cultivos"][codigo] = {
                "nombre": cultivo.nombre,
                "tipo": cultivo.tipo,
                "tipo_tierra": cultivo.tipo_tierra,
                "localidad": cultivo.localidad,
                "numero_parcela": cultivo.numero_parcela,
                "tamano_parcela": cultivo.tamano_parcela,
                "fecha_siembra": cultivo.fecha_siembra,
                "humedad": zona.sensor.leer(),
                "historial": [
                    {"momento": r.momento, "litros_estimados": r.litros_estimados, "motivo": r.motivo}
                    for r in zona.historial
                ],
            }
        guardar_datos(datos)

    def generar_codigo(self) -> str:
        self.contador += 1
        return f"CULT{self.contador:03d}"

    def registrar_cultivo(self, cultivo: Cultivo) -> ZonaRiego:
        config_zona = calcular_configuracion_zona(cultivo)
        sensor = SensorHumedad(humedad_inicial=HUMEDAD_INICIAL_POR_DEFECTO)
        valvula = Valvula(nombre=f"{cultivo.codigo}-{cultivo.nombre}")
        zona = ZonaRiego(cultivo=cultivo, config=config_zona, sensor=sensor, valvula=valvula)

        self.cultivos[cultivo.codigo] = cultivo
        self.zonas[cultivo.codigo] = zona
        self.guardar()
        return zona

    def eliminar_cultivo(self, codigo: str) -> bool:
        if codigo not in self.cultivos:
            return False
        del self.cultivos[codigo]
        del self.zonas[codigo]
        self.guardar()
        return True

    def buscar_por_codigo(self, codigo: str) -> Optional[ZonaRiego]:
        return self.zonas.get(codigo)

    def recalcular_configuraciones(self) -> None:
        """
        Vuelve a calcular los umbrales de cada zona (por ejemplo, la etapa de
        crecimiento cambia con el tiempo según fecha_siembra). Se llama antes
        de cada revisión de riego para que las decisiones sean siempre frescas.
        """
        for zona in self.zonas.values():
            zona.config = calcular_configuracion_zona(zona.cultivo)


# ============================================================
# CONTROLADOR: lógica de decisión (humedad + clima)
# ============================================================

class ControladorRiego:
    def __init__(self, gestor: GestorRiego, proveedor_clima: ProveedorClima):
        self.gestor = gestor
        self.proveedor_clima = proveedor_clima

    def revisar_y_regar_todas(self) -> None:
        if not self.gestor.zonas:
            logger.info("No hay cultivos registrados todavía. Nada que revisar.")
            return

        self.gestor.recalcular_configuraciones()

        pronostico = self.proveedor_clima.obtener_pronostico()
        logger.info(
            "Pronóstico: prob. lluvia=%.0f%%, mm esperados=%.1f, temp=%.1f°C",
            pronostico.probabilidad_lluvia * 100,
            pronostico.mm_lluvia_esperada,
            pronostico.temperatura_c,
        )

        if self._debe_posponerse_por_lluvia(pronostico):
            logger.info("Riego POSPUESTO en todas las zonas: se espera lluvia suficiente.")
            return

        for zona in self.gestor.zonas.values():
            self._revisar_zona(zona, pronostico)

        self.gestor.guardar()

    def _debe_posponerse_por_lluvia(self, pronostico: PronosticoClima) -> bool:
        return (
            pronostico.probabilidad_lluvia >= UMBRAL_PROBABILIDAD_LLUVIA
            and pronostico.mm_lluvia_esperada >= UMBRAL_MM_LLUVIA_ESPERADA
        )

    def _revisar_zona(self, zona: ZonaRiego, pronostico: PronosticoClima) -> None:
        humedad_actual = zona.sensor.leer()
        logger.info(
            "Cultivo '%s' (%s, etapa: %s): humedad actual = %.1f%% (mínimo: %.1f%%)",
            zona.cultivo.codigo, zona.cultivo.nombre, zona.config.etapa_crecimiento,
            humedad_actual, zona.config.humedad_minima,
        )

        if not zona.necesita_riego():
            logger.info("Cultivo '%s': humedad suficiente, no se riega.", zona.cultivo.codigo)
            return

        factor_ajuste = self._factor_ajuste_por_lluvia_leve(pronostico)
        self._regar_zona(zona, humedad_actual, factor_ajuste)

    def _factor_ajuste_por_lluvia_leve(self, pronostico: PronosticoClima) -> float:
        if pronostico.probabilidad_lluvia >= 0.3:
            return 0.7
        return 1.0

    def _regar_zona(self, zona: ZonaRiego, humedad_actual: float, factor_ajuste: float) -> None:
        deficit = zona.config.humedad_objetivo - humedad_actual
        minutos_estimados = min(
            zona.config.duracion_maxima_riego_min,
            max(1, round((deficit / 2.0) * factor_ajuste)),
        )

        logger.info("Cultivo '%s': iniciando riego por %d min (factor clima=%.1f)",
                    zona.cultivo.codigo, minutos_estimados, factor_ajuste)
        zona.valvula.abrir()

        litros = round(minutos_estimados * zona.config.caudal_litros_min, 1)
        zona.sensor.registrar_riego(incremento=deficit * factor_ajuste)

        zona.valvula.cerrar()

        zona.historial.append(RegistroRiego(
            momento=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            litros_estimados=litros,
            motivo="humedad por debajo del mínimo",
        ))

        logger.info("Cultivo '%s': riego finalizado. Litros estimados: %.1f, humedad final: %.1f%%",
                    zona.cultivo.codigo, litros, zona.sensor.leer())


# ============================================================
# ENTRADA DE DATOS (validaciones para el registro de cultivos)
# ============================================================

def pedir_texto_obligatorio(mensaje: str) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor == "":
            print("  Este dato es obligatorio, no puede quedar vacío. Intenta de nuevo.")
        else:
            return valor


def pedir_fecha_valida(mensaje: str) -> str:
    while True:
        valor = input(mensaje).strip()
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return valor
        except ValueError:
            print("  Fecha inválida. Debe tener el formato AAAA-MM-DD, ejemplo: 2026-08-19. Intenta de nuevo.")


def pedir_numero_positivo(mensaje: str) -> float:
    while True:
        valor = input(mensaje).strip()
        try:
            numero = float(valor)
            if numero <= 0:
                print("  El tamaño debe ser mayor a 0. Intenta de nuevo.")
            else:
                return numero
        except ValueError:
            print("  Eso no es un número válido. Escribe solo el número, ejemplo: 2.5. Intenta de nuevo.")


def normalizar_codigo(texto: str) -> str:
    """Acepta el código en varias formas ('CULT001', 'cult1', '001', '1') y lo normaliza."""
    texto = texto.strip().upper()
    if texto.startswith("CULT"):
        texto = texto[4:]
    if texto.isdigit():
        return f"CULT{int(texto):03d}"
    return texto


# ============================================================
# MENÚ PRINCIPAL
# ============================================================

gestor = GestorRiego()


def registrar_cultivo():
    print("\n--- Registrar nuevo cultivo ---")
    nombre = pedir_texto_obligatorio("Nombre del cultivo (ej. Maíz parcela 5): ")
    tipo = pedir_texto_obligatorio("Tipo de cultivo (ej. Maíz, Frijol, Café): ")
    tipo_tierra = pedir_texto_obligatorio("Tipo de tierra (ej. Arcillosa, Arenosa): ")
    localidad = pedir_texto_obligatorio("Localidad (ej. Chimaltenango): ")
    numero_parcela = pedir_texto_obligatorio("Número de parcela (ej. 3): ")
    tamano_parcela = pedir_numero_positivo("Tamaño de la parcela en hectáreas (ej. 2.5): ")
    fecha_siembra = pedir_fecha_valida("Fecha de siembra (formato AAAA-MM-DD, ej. 2026-08-19): ")

    cultivo = Cultivo(
        codigo=gestor.generar_codigo(),
        nombre=nombre,
        tipo=tipo,
        tipo_tierra=tipo_tierra,
        localidad=localidad,
        numero_parcela=numero_parcela,
        tamano_parcela=tamano_parcela,
        fecha_siembra=fecha_siembra,
    )
    zona = gestor.registrar_cultivo(cultivo)

    print(f"\nCultivo registrado: {cultivo.codigo}")
    print(f"Configuración de riego calculada -> humedad mínima: {zona.config.humedad_minima}%, "
          f"objetivo: {zona.config.humedad_objetivo}%, etapa: {zona.config.etapa_crecimiento}, "
          f"caudal: {zona.config.caudal_litros_min} L/min")


def ver_cultivos():
    if not gestor.zonas:
        print("\nNo hay cultivos registrados todavía.\n")
        return
    print("\n--- Cultivos y su estado de riego ---")
    gestor.recalcular_configuraciones()
    for zona in gestor.zonas.values():
        print(zona)
    print()


def buscar_cultivo():
    print("\n--- Buscar cultivo por código ---")
    codigo = normalizar_codigo(input("Escribe el código (ej. CULT001, cult1 o 001): "))
    zona = gestor.buscar_por_codigo(codigo)
    if zona:
        print(f"\n{zona.cultivo}")
        print(zona)
    else:
        print("No se encontró ningún cultivo con ese código.")


def eliminar_cultivo():
    print("\n--- Eliminar un cultivo ---")
    codigo = normalizar_codigo(input("Escribe el código del cultivo a eliminar: "))
    zona = gestor.buscar_por_codigo(codigo)
    if zona is None:
        print("No existe ningún cultivo con ese código.")
        return

    print(f"Cultivo encontrado: {zona.cultivo}")
    confirmacion = input("¿Seguro que quieres eliminarlo? Escribe 'sí' para confirmar: ").strip().lower()
    if confirmacion in ("sí", "si"):
        gestor.eliminar_cultivo(codigo)
        print("Cultivo eliminado correctamente.")
    else:
        print("Operación cancelada, el cultivo NO fue eliminado.")


def revisar_y_regar():
    controlador = ControladorRiego(gestor=gestor, proveedor_clima=PROVEEDOR_CLIMA)
    print(f"\nRevisando {len(gestor.zonas)} cultivo(s)...")
    controlador.revisar_y_regar_todas()
    print("Revisión finalizada.\n")


def ver_historial():
    print("\n--- Historial de riego por cultivo ---")
    if not gestor.zonas:
        print("No hay cultivos registrados todavía.\n")
        return
    for zona in gestor.zonas.values():
        if not zona.historial:
            continue
        print(f"\n{zona.cultivo.codigo} - {zona.cultivo.nombre}:")
        for evento in zona.historial:
            print(f"  - {evento.momento} | {evento.litros_estimados} L | {evento.motivo}")
    print()


def mostrar_menu():
    while True:
        print("\n===== Sistema de Riego Inteligente =====")
        print("1. Registrar un cultivo nuevo")
        print("2. Ver todos los cultivos y su estado de riego")
        print("3. Buscar un cultivo por código")
        print("4. Revisar y ejecutar riego (todos los cultivos)")
        print("5. Ver historial de riego")
        print("6. Eliminar un cultivo")
        print("7. Salir")

        opcion = input("Elige una opción (1-7): ").strip()

        if opcion == "1":
            registrar_cultivo()
        elif opcion == "2":
            ver_cultivos()
        elif opcion == "3":
            buscar_cultivo()
        elif opcion == "4":
            revisar_y_regar()
        elif opcion == "5":
            ver_historial()
        elif opcion == "6":
            eliminar_cultivo()
        elif opcion == "7":
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    mostrar_menu()
