# gestor_cultivos.py
# Este archivo se encarga de administrar TODOS los cultivos juntos:


from cultivo import Cultivo

class GestorCultivos:
    def __init__(self):
        # Esta lista vacía es donde se van a ir guardando todos los cultivos
        self.lista_cultivos = []

    def agregar_cultivo(self, cultivo):
        # Recibe un objeto Cultivo (ya creado) y lo agrega a la lista
        self.lista_cultivos.append(cultivo)
        print(f"Cultivo agregado: {cultivo.nombre}")

    def mostrar_todos(self):
        # Imprime todos los cultivos que hay hasta ahora
        if len(self.lista_cultivos) == 0:
            print("No hay cultivos registrados todavía.")
            return

        print("--- Lista de cultivos ---")
        for cultivo in self.lista_cultivos:
            print(cultivo)  # esto usa el __str__ que ya definimos en Cultivo

    def buscar_por_nombre(self, nombre_buscado):
        # --- BÚSQUEDA LINEAL ---
        # Esto es un algoritmo de búsqueda: revisa la lista UNO POR UNO
        # hasta encontrar un cultivo cuyo nombre coincida (o hasta terminar la lista).
        # Complejidad: O(n) -> en el peor caso revisa TODOS los cultivos.
        for cultivo in self.lista_cultivos:
            if cultivo.nombre.lower() == nombre_buscado.lower():
                # .lower() convierte todo a minúsculas, así "Maíz" y "maíz" se consideran iguales
                return cultivo  # lo encontramos, lo devolvemos de una vez

        return None  # si terminó el for y no encontró nada, devuelve None (nada)


# Zona de prueba
if __name__ == "__main__":
    gestor = GestorCultivos()

    # Creamos dos cultivos de prueba
    cultivo1 = Cultivo(
        codigo="CULT001",
        nombre="Maíz parcela 3",
        tipo="Maíz",
        tipo_tierra="Arcillosa",
        localidad="Chimaltenango",
        fecha_siembra="2026-08-18"
    )

    cultivo2 = Cultivo(
        codigo="CULT002",
        nombre="Frijol parcela 1",
        tipo="Frijol",
        tipo_tierra="Arenosa",
        localidad="Chimaltenango",
        fecha_siembra="2026-08-19"
    )

    # Los agregamos al gestor
    gestor.agregar_cultivo(cultivo1)
    gestor.agregar_cultivo(cultivo2)

    # Mostramos la lista completa
    gestor.mostrar_todos()

    # --- Probamos la búsqueda ---
    print("\nBuscando 'Frijol parcela 1'...")
    resultado = gestor.buscar_por_nombre("Frijol parcela 1")
    if resultado:
        print(f"¡Encontrado! {resultado}")
    else:
        print("No se encontró ese cultivo.")

    print("\nBuscando 'Tomate parcela 5' (que no existe)...")
    resultado2 = gestor.buscar_por_nombre("Tomate parcela 5")
    if resultado2:
        print(f"¡Encontrado! {resultado2}")
    else:
        print("No se encontró ese cultivo.")