class PilaMovimientos:
    """
    Pila de movimientos del inventario.

    Funciona con el principio LIFO:
    El último movimiento que entra es el primero que sale.
    """

    def __init__(self):
        self.movimientos = []

    def apilar(self, movimiento):
        """
        Agrega un movimiento a la pila.
        """
        self.movimientos.append(movimiento)

    def desapilar(self):
        """
        Elimina y devuelve el último movimiento de la pila.
        """
        if self.esta_vacia():
            return None

        return self.movimientos.pop()

    def cima(self):
        """
        Devuelve el último movimiento sin eliminarlo.
        """
        if self.esta_vacia():
            return None

        return self.movimientos[-1]

    def esta_vacia(self):
        """
        Comprueba si la pila está vacía.
        """
        return len(self.movimientos) == 0

    def cantidad(self):
        """
        Devuelve la cantidad de movimientos almacenados.
        """
        return len(self.movimientos)

    def limpiar(self):
        """
        Elimina todos los movimientos de la pila.
        """
        self.movimientos.clear()

    def mostrar(self):
        """
        Devuelve una copia de los movimientos almacenados.
        """
        return self.movimientos.copy()