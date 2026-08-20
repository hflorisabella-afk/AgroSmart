# clima.py
# Este archivo define qué es un "Clima" dentro de AgroSmart.
# Representa la información del clima para una localidad en un momento dado
# (esta info normalmente vendrá de una API externa, pero así es como la guardamos).

class Clima:
    def __init__(self, localidad, temperatura, probabilidad_lluvia, descripcion=""):
        self.localidad = localidad                       # ej: "Chimaltenango"
        self.temperatura = temperatura                    # ej: 28 (en grados Celsius)
        self.probabilidad_lluvia = probabilidad_lluvia    # ej: 70 (en porcentaje)
        self.descripcion = descripcion                    # ej: "Parcialmente nublado"

    def generar_alerta(self):
        # Esta función revisa los datos y decide si hay que mostrar una alerta.
        # Aquí es donde el sistema "se ve inteligente".
        if self.probabilidad_lluvia >= 70:
            return "🌧️ Alerta: se esperan lluvias fuertes."
        elif self.temperatura >= 32:
            return "☀️ Alerta: temperatura muy alta, revisa tus cultivos."
        else:
            return "✅ Sin alertas por ahora."

    def __str__(self):
        return f"{self.localidad}: {self.temperatura}°C, {self.probabilidad_lluvia}% de lluvia"


# --- Zona de prueba ---
if __name__ == "__main__":
    clima1 = Clima(
        localidad="Chimaltenango",
        temperatura=33,
        probabilidad_lluvia=20,
        descripcion="Soleado"
    )

    print(clima1)
    print(clima1.generar_alerta())