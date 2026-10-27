# AgroSmart – Sistema Inteligente para Agricultura

AgroSmart es una aplicación de escritorio hecha en **Python con Kivy** 
que ayuda a un agricultor a registrar sus cultivos, consultar el clima, planificar el riego, organizar actividades 
y llevar su inventario. Es un proyecto universitario (Proyecto 6: *Sistema Inteligente para Agricultura*) que aplica estructuras de datos y algoritmos en 
un problema real.

****Integrantes:** Flor Isabella Hernández Gómez, Kímberly Nahomi Pixtun Martir, Kenneth Gabriel Garcia Cruz,Marcos Adrián Soto Alvarez, Dilan Antonio López Juárez.** 
## Pantallas de la aplicación

| Pantalla | Qué hace |
|---|---|
| **Cultivos** | Registra, busca, ordena, edita y elimina cultivos (con tamaño en manzanas, cuerdas o hectáreas). |
| **Clima** | Consulta el clima actual y el pronóstico de 5 días para la localidad del cultivo, con alertas. Usa la API gratuita Open-Meteo. |
| **Riego** | Riego con sensor simulado y plan de agua: recomendación de litros, riegos pendientes y hechos, reparto de agua y recorrido entre parcelas. |
| **Calendario** | Actividades por cultivo ordenadas por fecha y predicción de la fecha de cosecha. |
| **Inventario** | Registro de productos con opción de deshacer movimientos. |

## Cómo instalar y ejecutar

1. Instalar Python 3.11 o superior.
2. Instalar las dependencias:

```
pip install -r Codigo/requirements.txt
```

3. Ejecutar la aplicación:

```
python Codigo/app_principal.py
```

La pantalla de Clima necesita conexión a internet. Todo lo demás funciona sin conexión. Los datos se guardan en archivos JSON dentro de `Codigo/`, así que no se pierden al cerrar el programa.

## Estructuras de datos y algoritmos

| Estructura | Dónde se usa |
|---|---|
| Arreglo (lista) | Lista de cultivos y de productos |
| Tabla hash | Buscar un cultivo por su código |
| Pila | Botón "Deshacer" del Inventario |
| Cola | Riegos pendientes (Riego) |
| Lista enlazada | Historial de riegos hechos (Riego) |
| Árbol binario de búsqueda | Eventos del Calendario ordenados por fecha |
| Grafo | Distancias entre la casa y las parcelas (Riego) |

| Algoritmo | Tipo | Dónde se usa |
|---|---|---|
| Búsqueda lineal | Búsqueda | Cultivos → Buscar cultivo |
| Búsqueda binaria | Búsqueda | Cultivos → Buscar por nombre exacto |
| Ordenamiento por inserción | Ordenamiento | Cultivos → Ordenar por fecha de siembra |
| Merge Sort | Ordenamiento | Riego → Repartir mi agua (y pronóstico en `clima.py`) |
| Dijkstra | Grafos | Riego → Camino más corto |
| Voraz (greedy) | Optimización | Riego → Repartir mi agua y mejor orden de visita |

Cada algoritmo tiene su pseudocódigo, diagrama de flujo, análisis de complejidad (tiempo y espacio) y justificación en la carpeta `ManualTecnico/`.

## Estructura del repositorio

```
Codigo/
  app_principal.py      Ventana principal con la barra de pantallas
  algoritmos/           Dijkstra, Merge Sort, algoritmo voraz
  estructuras/          Pila, cola, lista enlazada, árbol, grafo, tabla hash
  modelos/              Lógica de cultivos, calendario, inventario, clima y planificador
  pantallas/            Pantallas de Kivy
  riego/                Módulo y pantalla de riego
Diagramas/              Diagramas de flujo de los algoritmos
ManualTecnico/          Análisis de algoritmos y estructuras por módulo
ManualUsuario/          Manual de usuario por módulo
Documentacion/          Índice de la documentación
Propuesta/              Propuesta del proyecto
```

## Documentación

- **Manuales técnicos** (`ManualTecnico/`): Cultivos, Riego, Clima, Calendario, Inventario y `Algoritmos_y_Estructuras`.
- **Manuales de usuario** (`ManualUsuario/`): uno por cada pantalla, con instrucciones paso a paso.

## Notas

- El sensor de humedad, la válvula y el clima de la pantalla Riego son una **simulación**: el sistema **no**
está conectado a aparatos reales.
- La predicción de cosecha es una estimación según el tipo de cultivo y su fecha de siembra.
