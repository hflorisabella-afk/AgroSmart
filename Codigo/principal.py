import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "modelos"))

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos

gestor = GestorCultivos()


def pedir_texto_obligatorio(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor == "":
            print(" Este dato es obligatorio, no puede quedar vacío. Intenta de nuevo.")
        else:
            return valor


def pedir_fecha_valida(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return valor
        except ValueError:
            print("  Fecha inválida. Debe tener el formato AAAA-MM-DD, ejemplo: 2026-08-19. Intenta de nuevo.")


def pedir_numero_positivo(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            numero = float(valor)
            if numero <= 0:
                print("️  El tamaño debe ser mayor a 0. Intenta de nuevo.")
            else:
                return numero
        except ValueError:
            print("  Eso no es un número válido. Escribe solo el número, ejemplo: 2.5. Intenta de nuevo.")


def registrar_cultivo():
    print("\n--- Registrar nuevo cultivo ---")
    nombre = pedir_texto_obligatorio("Nombre del cultivo (ej. Maíz parcela 5): ")
    tipo = pedir_texto_obligatorio("Tipo de cultivo (ej. Maíz, Frijol, Café): ")
    tipo_tierra = pedir_texto_obligatorio("Tipo de tierra (ej. Arcillosa, Arenosa): ")
    localidad = pedir_texto_obligatorio("Localidad (ej. Chimaltenango): ")
    numero_parcela = pedir_texto_obligatorio("Número de parcela (ej. 3): ")
    tamano_parcela = pedir_numero_positivo("Tamaño de la parcela en hectáreas (ej. 2.5): ")
    fecha_siembra = pedir_fecha_valida("Fecha de siembra (formato AAAA-MM-DD, ej. 2026-08-19): ")

    nuevo_cultivo = Cultivo(
        codigo=gestor.generar_codigo(),
        nombre=nombre,
        tipo=tipo,
        tipo_tierra=tipo_tierra,
        localidad=localidad,
        numero_parcela=numero_parcela,
        tamano_parcela=tamano_parcela,
        fecha_siembra=fecha_siembra
    )

    gestor.agregar_cultivo(nuevo_cultivo)


def buscar_cultivo():
    print("\n--- Buscar cultivo ---")
    nombre_buscado = input("Escribe el nombre del cultivo a buscar: ")
    resultado = gestor.buscar_por_nombre(nombre_buscado)
    if resultado:
        print(f"¡Encontrado! {resultado}")
    else:
        print("No se encontró ningún cultivo con ese nombre.")


def buscar_cultivo_por_codigo():
    print("\n--- Buscar cultivo por código ---")
    codigo_buscado = input("Escribe el código del cultivo (ej. CULT001): ").strip()
    resultado = gestor.buscar_por_codigo_hash(codigo_buscado)
    if resultado:
        print(f"¡Encontrado! {resultado}")
    else:
        print("No se encontró ningún cultivo con ese código.")


def buscar_cultivo_binaria():
    print("\n--- Buscar cultivo por nombre (búsqueda binaria) ---")
    nombre_buscado = input("Escribe el nombre exacto del cultivo a buscar: ")
    resultado = gestor.buscar_por_nombre_binaria(nombre_buscado)
    if resultado:
        print(f"¡Encontrado! {resultado}")
    else:
        print("No se encontró ningún cultivo con ese nombre.")


def mostrar_menu():
    while True:
        print("\n===== AGROSMART - Registro de cultivos =====")
        print("1. Registrar un cultivo nuevo")
        print("2. Ver todos los cultivos")
        print("3. Buscar un cultivo por nombre (búsqueda lineal)")
        print("4. Ordenar cultivos por fecha de siembra")
        print("5. Buscar un cultivo por código (búsqueda rápida)")
        print("6. Buscar un cultivo por nombre (búsqueda binaria)")
        print("7. Salir")

        opcion = input("Elige una opción (1-7): ")

        if opcion == "1":
            registrar_cultivo()
        elif opcion == "2":
            gestor.mostrar_todos()
        elif opcion == "3":
            buscar_cultivo()
        elif opcion == "4":
            gestor.ordenar_por_fecha_siembra()
            print("\n Cultivos ordenados por fecha de siembra (del más antiguo al más reciente):")
            gestor.mostrar_todos()
        elif opcion == "5":
            buscar_cultivo_por_codigo()
        elif opcion == "6":
            buscar_cultivo_binaria()
        elif opcion == "7":
            print("¡Hasta luego! ")
            break
        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    mostrar_menu()