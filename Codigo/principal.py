# principal.py
# Este archivo es un "menú de texto" temporal.
# Sirve para probar que toda la lógica funciona ANTES de hacer la pantalla bonita con Kivy.
# El agricultor (por ahora, nosotros probando) escribe sus datos aquí, en la terminal.
#
# Este archivo debe estar en Codigo/, al mismo nivel que la carpeta modelos/
# (NO adentro de modelos/, sino al lado).

import sys
import os
from datetime import datetime  # esto nos sirve para revisar que la fecha sea válida de verdad

# Esta línea le dice a Python "también busca archivos dentro de la carpeta modelos"
# Así podemos usar Cultivo y GestorCultivos sin mover nada de lugar.
sys.path.append(os.path.join(os.path.dirname(__file__), "modelos"))

from cultivo import Cultivo
from gestor_cultivos import GestorCultivos

# Creamos UN solo gestor que va a vivir mientras el programa esté abierto
gestor = GestorCultivos()


def pedir_texto_obligatorio(mensaje):
    # Esta función NO deja pasar un campo vacío.
    # Sigue preguntando hasta que el agricultor escriba algo de verdad.
    while True:
        valor = input(mensaje).strip()  # .strip() quita espacios en blanco de sobra
        if valor == "":
            print(" Este dato es obligatorio, no puede quedar vacío. Intenta de nuevo.")
        else:
            return valor


def pedir_fecha_valida(mensaje):
    # Esta función NO deja pasar una fecha con formato incorrecto.
    # Solo acepta fechas con formato AAAA-MM-DD (ej. 2026-08-19), y que además existan de verdad
    # (no deja pasar cosas como "2026-19-40", que tendría un mes y día imposibles).
    while True:
        valor = input(mensaje).strip()
        try:
            datetime.strptime(valor, "%Y-%m-%d")
            return valor  # si no lanzó error, la fecha es válida
        except ValueError:
            print("Fecha inválida. Debe tener el formato AAAA-MM-DD, ejemplo: 2026-08-19. Intenta de nuevo.")


def pedir_numero_positivo(mensaje):
    # Esta función NO deja pasar algo que no sea un número, ni números negativos o cero.
    # Sirve para el tamaño de la parcela (ej. hectáreas): tiene que ser un número real y mayor a 0.
    while True:
        valor = input(mensaje).strip()
        try:
            numero = float(valor)  # intenta convertir el texto a número decimal
            if numero <= 0:
                print("⚠️  El tamaño debe ser mayor a 0. Intenta de nuevo.")
            else:
                return numero
        except ValueError:
            print("⚠️  Eso no es un número válido. Escribe solo el número, ejemplo: 2.5. Intenta de nuevo.")


def registrar_cultivo():
    print("\n--- Registrar nuevo cultivo ---")
    # Ya NO le preguntamos el código al agricultor, el sistema lo genera solo.
    # Usamos las funciones de validación para cada campo.
    nombre = pedir_texto_obligatorio("Nombre del cultivo (ej. Maíz ): ")
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


def mostrar_menu():
    while True:
        print("\n===== AGROSMART - Registro de cultivos =====")
        print("1. Registrar un cultivo nuevo")
        print("2. Ver todos los cultivos")
        print("3. Buscar un cultivo por nombre")
        print("4. Salir")

        opcion = input("Elige una opción (1-4): ")

        if opcion == "1":
            registrar_cultivo()
        elif opcion == "2":
            gestor.mostrar_todos()
        elif opcion == "3":
            buscar_cultivo()
        elif opcion == "4":
            print("¡Hasta luego! ")
            break
        else:
            print("Opción no válida, intenta de nuevo.")


if __name__ == "__main__":
    mostrar_menu()