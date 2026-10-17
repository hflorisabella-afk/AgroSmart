# clima.py
# Modulo de Clima y Alertas - AgroSmart
# Usa la API gratuita de Open-Meteo (no requiere API key).
# Instalar antes: pip install requests
#
# La ubicacion se puede dar de 3 formas:
#   1. Nombre de cualquier lugar: municipio, aldea, caserio, finca, ciudad, pais...
#      (ej: "Chimaltenango", "Aldea San Jose Poaquil", "Antigua Guatemala")
#   2. Coordenadas "latitud, longitud" (ej: "14.6569, -90.8206"), sirve para
#      cualquier punto del mapa, incluso donde no hay nombre registrado.
#   3. Ubicacion actual (texto vacio, "aqui" o "mi ubicacion"): se detecta por IP.

import re
import requests
import time
from modelos.ordenamiento_clima import merge_sort

# Ubicacion que se usa si no se puede detectar la actual
LOCALIDAD_POR_DEFECTO = "Chimaltenango"

# Pais donde se busca primero cuando un nombre es ambiguo (codigo de 2 letras).
# "gt" = Guatemala. Ponlo en None para buscar en todo el mundo sin preferencia.
PAIS_PREFERIDO = "gt"


class Clima:
    def __init__(self, localidad, temperatura, probabilidad_lluvia, descripcion=""):
        self.localidad = localidad  # ej: "Chimaltenango"
        self.temperatura = temperatura  # ej: 28 (en grados Celsius)
        self.probabilidad_lluvia = probabilidad_lluvia  # ej: 70 (en porcentaje)
        self.descripcion = descripcion  # ej: "Parcialmente nublado"

    def generar_alerta(self):
        # Esta funcion revisa los datos y decide si hay que mostrar una alerta.
        lluvia_fuerte = self.probabilidad_lluvia >= 70
        calor_extremo = self.temperatura >= 32
        sequia = self.probabilidad_lluvia < 30 and self.temperatura >= 30

        if lluvia_fuerte and calor_extremo:
            return "️ Alerta doble: lluvias fuertes y temperatura muy alta. Protege tus cultivos."
        elif lluvia_fuerte:
            return " Alerta: se esperan lluvias fuertes."
        elif calor_extremo:
            return "️ Alerta: temperatura muy alta, revisa tus cultivos."
        elif sequia:
            return " Alerta: poca probabilidad de lluvia y calor alto, considera regar tus plantas."
        else:
            return " Sin alertas por ahora."

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


# --- Resolucion de ubicaciones (nombre, coordenadas o ubicacion actual) ---

# Patron para textos como "14.6569, -90.8206" o "14.6569 -90.8206"
_PATRON_COORDENADAS = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*[,;\s]\s*(-?\d+(?:\.\d+)?)\s*$")

# Textos que significan "usa donde estoy ahora"
_TEXTOS_UBICACION_ACTUAL = {"", "aqui", "aquí", "mi ubicacion", "mi ubicación", "ubicacion actual", "ubicación actual"}


def _leer_coordenadas(texto):
    """Si el texto son coordenadas validas devuelve (lat, lon); si no, None."""
    coincidencia = _PATRON_COORDENADAS.match(texto)
    if not coincidencia:
        return None
    lat = float(coincidencia.group(1))
    lon = float(coincidencia.group(2))
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Las coordenadas estan fuera de rango (lat -90 a 90, lon -180 a 180)")
    return lat, lon


def obtener_ubicacion_actual():
    """
    Detecta la ubicacion aproximada del usuario a partir de su IP
    (servicio gratuito ipwho.is, sin API key). Devuelve (lat, lon, nombre).
    Es aproximada: puede marcar la ciudad del proveedor de internet.
    """
    en_cache = _obtener_de_cache("ubicacion_actual")
    if en_cache is not None:
        return en_cache

    respuesta = requests.get("https://ipwho.is/", timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if not datos.get("success", False):
        raise ValueError("No se pudo detectar tu ubicacion actual")

    nombre = datos.get("city") or datos.get("region") or datos.get("country") or "Ubicacion actual"
    resultado = (datos["latitude"], datos["longitude"], nombre)

    _guardar_en_cache("ubicacion_actual", resultado)
    return resultado


def _buscar_en_open_meteo(nombre):
    """Geocodificador 1 (rapido, ciudades y municipios). Devuelve (lat, lon, nombre) o None."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": nombre, "count": 1, "language": "es"}

    respuesta = requests.get(url, params=params, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if "results" not in datos or len(datos["results"]) == 0:
        return None

    r = datos["results"][0]
    return r["latitude"], r["longitude"], r.get("name", nombre)


def _buscar_en_nominatim(nombre, pais=None):
    """
    Geocodificador 2: OpenStreetMap (Nominatim). Conoce muchisimos mas lugares:
    aldeas, caserios, fincas, colonias, calles, negocios, etc.
    Devuelve (lat, lon, nombre) o None.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": nombre, "format": "jsonv2", "limit": 1, "accept-language": "es"}
    if pais:
        params["countrycodes"] = pais
    # Nominatim exige identificarse con un User-Agent propio
    cabeceras = {"User-Agent": "AgroSmart/1.0 (proyecto escolar)"}

    respuesta = requests.get(url, params=params, headers=cabeceras, timeout=10)
    respuesta.raise_for_status()
    datos = respuesta.json()

    if len(datos) == 0:
        return None

    r = datos[0]
    nombre_mostrar = r.get("name") or r.get("display_name", nombre).split(",")[0]
    return float(r["lat"]), float(r["lon"]), nombre_mostrar


def _buscar_por_nombre(nombre):
    """
    Busca un nombre de lugar en varios servicios, de mas a menos preciso:
      1. Open-Meteo (municipios y ciudades)
      2. OpenStreetMap en PAIS_PREFERIDO (aldeas, fincas, colonias...)
      3. OpenStreetMap en todo el mundo
    Devuelve (lat, lon, nombre) o None si ninguno lo conoce.
    """
    encontrado = _buscar_en_open_meteo(nombre)
    if encontrado is not None:
        return encontrado

    if PAIS_PREFERIDO:
        encontrado = _buscar_en_nominatim(nombre, PAIS_PREFERIDO)
        if encontrado is not None:
            return encontrado
        time.sleep(1)  # Nominatim permite maximo 1 consulta por segundo

    return _buscar_en_nominatim(nombre)


def resolver_ubicacion(entrada):
    """
    Convierte lo que escriba el usuario en (latitud, longitud, nombre_para_mostrar).
    Acepta: nombre de cualquier lugar, coordenadas o ubicacion actual.
    Si el lugar exacto no existe (ej: "Finca El Sol, Chimaltenango") prueba con
    las partes mas generales hasta encontrar algo.
    """
    texto = (entrada or "").strip()
    clave_cache = f"ubicacion:{texto.lower()}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    # 1. Ubicacion actual
    if texto.lower() in _TEXTOS_UBICACION_ACTUAL:
        resultado = obtener_ubicacion_actual()

    else:
        # 2. Coordenadas directas
        coordenadas = _leer_coordenadas(texto)
        if coordenadas is not None:
            lat, lon = coordenadas
            resultado = (lat, lon, f"{lat:.4f}, {lon:.4f}")

        else:
            # 3. Nombre de lugar: primero el texto completo y, si no aparece,
            # las partes separadas por coma de derecha a izquierda (de lo
            # general a lo especifico)
            intentos = [texto]
            partes = [p.strip() for p in texto.split(",") if p.strip()]
            if len(partes) > 1:
                intentos.extend(reversed(partes))

            resultado = None
            for intento in intentos:
                encontrado = _buscar_por_nombre(intento)
                if encontrado is not None:
                    resultado = encontrado
                    break

            if resultado is None:
                raise ValueError(
                    f"No se encontro la ubicacion '{texto}'. "
                    "Prueba con otro nombre o escribe las coordenadas (ej: 14.6569, -90.8206)."
                )

    _guardar_en_cache(clave_cache, resultado)
    return resultado


def obtener_coordenadas(localidad):
    """
    Devuelve (latitud, longitud) para cualquier ubicacion: nombre, coordenadas
    o ubicacion actual. Se mantiene para no romper el resto del proyecto.
    """
    lat, lon, _ = resolver_ubicacion(localidad)
    return lat, lon


def obtener_clima_actual(localidad):
    """
    Devuelve un objeto Clima con la temperatura y probabilidad de lluvia
    actuales para la ubicacion indicada (nombre, coordenadas o ubicacion
    actual). Usa cache para no pedir datos nuevos si ya se consulto hace poco.
    """
    clave_cache = f"actual:{(localidad or '').strip().lower()}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    try:
        lat, lon, nombre = resolver_ubicacion(localidad)

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

        clima = Clima(nombre, temperatura, probabilidad_lluvia, descripcion)
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
    Acepta nombre, coordenadas o ubicacion actual.
    """
    clave_cache = f"pronostico:{(localidad or '').strip().lower()}:{dias}"
    en_cache = _obtener_de_cache(clave_cache)
    if en_cache is not None:
        return en_cache

    try:
        lat, lon, nombre = resolver_ubicacion(localidad)

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

            clima_dia = Clima(f"{nombre} ({fecha})", temperatura, probabilidad_lluvia, descripcion)
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
    print("Puedes escribir:")
    print("  - Un lugar (municipio, aldea, finca, ciudad...): Chimaltenango")
    print("  - Coordenadas: 14.6569, -90.8206")
    print("  - Nada (Enter) para usar tu ubicacion actual")
    localidad = input("¿Dónde está tu cultivo? ").strip()

    if not localidad:
        # Sin texto: se intenta detectar la ubicacion actual; si falla, se usa el valor por defecto
        try:
            obtener_ubicacion_actual()
        except (requests.exceptions.RequestException, ValueError):
            print(f"No se pudo detectar tu ubicacion, se usara {LOCALIDAD_POR_DEFECTO}.")
            localidad = LOCALIDAD_POR_DEFECTO

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

        print()
        print("--- Pronostico ordenado por temperatura (Merge Sort) ---")
        for dia in merge_sort(pronostico, clave="temperatura"):
            print(dia)

        print()
        print("--- Pronostico ordenado por probabilidad de lluvia (Merge Sort) ---")
        for dia in merge_sort(pronostico, clave="probabilidad_lluvia"):
            print(dia)