# clima.py
# Modulo de Clima y Alertas - AgroSmart
# Usa la API gratuita de Open-Meteo (no requiere API key).

import requests
import time


class Clima:
    def __init__(self, localidad, temperatura, probabilidad_lluvia, descripcion=""):
        self.localidad = localidad                        # ej: "Chimaltenango"
        self.temperatura = temperatura                     # ej: 28 (en grados Celsius)
        self.probabilidad_lluvia = probabilidad_lluvia     # ej: 70 (en porcentaje)
        self.descripcion = descripcion                     # ej: "Parcialmente nublado"

    def generar_alerta(self):
        # Esta funcion revisa los datos y decide si hay que mostrar una alerta.
        lluvia_fuerte = self.probabilidad_lluvia >= 70
        calor_extremo = self.temperatura >= 32
        sequia = self.probabilidad_lluvia < 30 and self.temperatura >= 30

        if lluvia_fuerte and calor_extremo:
            return "⚠️ Alerta doble: lluvias fuertes y temperatura muy alta. Protege tus cultivos."
        elif lluvia_fuerte:
            return "🌧️ Alerta: se esperan lluvias fuertes."
        elif calor_extremo:
            return "☀️ Alerta: temperatura muy alta, revisa tus cultivos."
        elif sequia:
            return "🌵 Alerta: poca probabilidad de lluvia y calor alto, considera regar tus plantas."
        else:
            return "✅ Sin alertas por ahora."

    def necesita_riego(self):
        return self.temperatura >= 30 and self.probabilidad_lluvia < 30

    def __str__(self):
        return f"{self.localidad}: {self.temperatura}°C, {self.probabilidad_lluvia}% de lluvia ({self.descripcion})"


# --- Codigos de clima de Open-Meteo traducidos a descripcion en español ---
CODIGOS_CLIMA = {
    0: "Despejado",
    1: "Mayormente despejado",
    2: "Parcialmente nublado",
    3: "Nublado",
    45: "Neblina",
    48: "Neblina con escarcha",
    51: "Llovizna ligera",
    53: "Llovizna moderada",
    55: "Llovizna intensa",
    61: "Lluvia ligera",
    63: "Lluvia moderada",
    65: "Lluvia fuerte",
    80: "Chubascos ligeros",
    81: "Chubascos moderados",
    82: "Chubascos fuertes",
    95: "Tormenta",
}

# --- Cache simple en memoria ---
# Guarda el ultimo resultado por localidad durante X minutos,
# para no golpear la API cada vez que alguien del equipo corre el programa.
_CACHE = {}
_DURACION_CACHE_SEGUNDOS = 10 * 60  # 10 minutos


def _obtener_de_cache(clave):
    if clave in _CACHE:
        valor, guardado_en = _CACHE[clave]
        if time.time() - guardado_en < _DURACION_CACHE_SEGUNDOS:
            return valor
    return None


def _guardar_en_cache(clave, valor):
    _CACHE[clave] = (valor, time.time())


def obtener_coordenadas(localidad):
    """
    Convierte el nombre de una localidad (ej: "Chimaltenango") en
    latitud/longitud usando el geocodificador gratuito de Open-Meteo.
    """
    clave_cache = f"coords:{localidad.lower()}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": localidad, "count": 1, "language": "es"}

    respuesta = requests.get(url, params=params, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if "results" not in datos or len(datos["results"]) == 0:
        raise ValueError(f"No se encontro la localidad '{localidad}'")

    resultado = datos["results"][0]
    coordenadas = (resultado["latitude"], resultado["longitude"])

    _guardar_en_cache(clave_cache, coordenadas)
    return coordenadas


def obtener_clima_actual(localidad):
    """
    Devuelve un objeto Clima con la temperatura y probabilidad de lluvia
    actuales para la localidad indicada. Usa cache para no pedir datos
    nuevos si ya se consulto hace poco.
    """
    clave_cache = f"actual:{localidad.lower()}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    try:
        lat, lon = obtener_coordenadas(localidad)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,precipitation_probability,weather_code",
            "timezone": "auto",
        }

        respuesta = requests.get(url, params=params, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        actual = datos["current"]
        temperatura = actual["temperature_2m"]
        probabilidad_lluvia = actual.get("precipitation_probability", 0)
        codigo = actual.get("weather_code", 0)
        descripcion = CODIGOS_CLIMA.get(codigo, "Sin descripcion")

        clima = Clima(localidad, temperatura, probabilidad_lluvia, descripcion)
        _guardar_en_cache(clave_cache, clima)
        return clima

    except requests.exceptions.RequestException:
        print("No se pudo conectar con el servicio de clima. Revisa tu conexion a internet.")
        return None
    except (KeyError, ValueError) as error:
        print(f"No se pudo obtener el clima: {error}")
        return None


def obtener_pronostico_dias(localidad, dias=5):
    """
    Devuelve una lista de objetos Clima, uno por cada dia del pronostico
    (temperatura maxima y probabilidad de lluvia de ese dia). Usa cache.
    """
    clave_cache = f"pronostico:{localidad.lower()}:{dias}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    try:
        lat, lon = obtener_coordenadas(localidad)

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "temperature_2m_max,precipitation_probability_max,weather_code",
            "timezone": "auto",
            "forecast_days": dias,
        }

        respuesta = requests.get(url, params=params, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()

        diario = datos["daily"]
        lista_climas = []

        for i in range(len(diario["time"])):
            fecha = diario["time"][i]
            temperatura = diario["temperature_2m_max"][i]
            probabilidad_lluvia = diario["precipitation_probability_max"][i]
            codigo = diario["weather_code"][i]
            descripcion = CODIGOS_CLIMA.get(codigo, "Sin descripcion")

            clima_dia = Clima(f"{localidad} ({fecha})", temperatura, probabilidad_lluvia, descripcion)
            lista_climas.append(clima_dia)

        _guardar_en_cache(clave_cache, lista_climas)
        return lista_climas

    except requests.exceptions.RequestException:
        print("No se pudo conectar con el servicio de clima. Revisa tu conexion a internet.")
        return []
    except (KeyError, ValueError) as error:
        print(f"No se pudo obtener el pronostico: {error}")
        return []


def generar_pronostico(lista_climas):
    """Arma un resumen de texto con la alerta de cada dia."""
    resumen = []
    for clima_dia in lista_climas:
        resumen.append(f"{clima_dia} -> {clima_dia.generar_alerta()}")
    return "\n".join(resumen)


# --- Zona de prueba ---
if __name__ == "__main__":
    localidad = input("¿En qué localidad está tu cultivo? ").strip()
    if not localidad:
        localidad = "Chimaltenango"  # valor por defecto si no escriben nada

    print("--- Clima actual ---")
    clima_actual = obtener_clima_actual(localidad)
    if clima_actual:
        print(clima_actual)
        print(clima_actual.generar_alerta())
        print("¿Necesita riego?", clima_actual.necesita_riego())

    print()
    print("--- Pronostico de 5 dias ---")
    pronostico = obtener_pronostico_dias(localidad, dias=5)
    if pronostico:
        print(generar_pronostico(pronostico))