# Informe Técnico: Planificador de Rutas con Estrategia Greedy
**Alumnos:** Flory y Cuomo
**Materia:** Programación III (UADE)

## 1. Introducción
El presente trabajo práctico implementa un planificador de movimientos para un robot cuadrúpedo (Unitree Go2 / G1) utilizando una **estrategia Greedy (ávida)**. El objetivo principal es analizar el comportamiento de este enfoque heurístico puro en diferentes topologías de mapas, observando cómo las decisiones basadas únicamente en el óptimo local (minimizar la distancia al destino en cada paso) pueden derivar en rutas exitosas, rutas subóptimas o bloqueos irreversibles.

## 2. Detalles de la Implementación
El algoritmo fue desarrollado en Python y se estructura de la siguiente manera:
1. **Representación del Entorno:** La grilla se representa como una matriz 2D donde `0` es transitable y valores `1` o `2` representan obstáculos o zonas prohibidas.
2. **Función de Selección y Heurística:** En cada paso, el robot evalúa sus vecinos ortogonales válidos (dentro de los límites, sin obstáculos y **no visitados previamente** para evitar bucles infinitos inmediatos). Para cada candidato, calcula la **Distancia Manhattan** al objetivo: `distancia = abs(fila - filaDestino) + abs(columna - columnaDestino)`.
3. **Criterio de Desempate Estricto:** Si varios candidatos viables poseen la misma distancia mínima calculada, el algoritmo aplica un orden de precedencia fijo (ARRIBA $\rightarrow$ DERECHA $\rightarrow$ ABAJO $\rightarrow$ IZQUIERDA).
4. **Traducción Cinemática:** Una vez resuelta la ruta en coordenadas matriz, se traduce a comandos físicos (`AVANZAR`, `GIRAR DERECHA 90°`, `GIRAR 180°`, `GIRAR IZQUIERDA 90°`), tomando en consideración el tamaño de la celda en metros y la orientación dinámica del robot.

## 3. Análisis de Casos de Prueba

### Mapa 1 - Solución directa
- **Resultado:** `DESTINO_ALCANZADO` en **8 pasos**.
- **Análisis:** En este escenario, la topología del mapa permite que cada elección local (la que reduce la distancia Manhattan) coincida con la ruta global óptima. El robot avanzó sin requerir alejarse del destino en ningún momento. Es el caso ideal para un algoritmo voraz.

### Mapa 2 - Solución no óptima
- **Resultado:** `DESTINO_ALCANZADO` en **20 pasos**.
- **Análisis:** Aunque el robot logró llegar al destino, lo hizo recorriendo una ruta considerablemente más larga (20 movimientos) que la óptima posible (12 movimientos). Esto sucede porque el algoritmo prioriza siempre la celda que minimiza la distancia momentánea. Al encontrarse con una pared de obstáculos en su descenso (`Fila 5`), se vio forzado a bordearla retrocediendo en columnas pero manteniendo el estado "válido". El desempate estricto forzó el rodeo. Esto ilustra una de las principales limitaciones de Greedy: al no tener visión a futuro ni revisar decisiones anteriores, el óptimo local no garantiza el óptimo global.

### Mapa 3 - Fracaso de la estrategia
- **Resultado:** `BLOQUEADO` en el paso **12**.
- **Análisis:** El robot avanzó hacia el objetivo atraído por la reducción de la distancia Manhattan hasta llegar a la coordenada `(6, 4)`. En ese punto, todos sus vecinos inmediatos eran obstáculos, celdas prohibidas o celdas ya visitadas. Aunque existía un camino válido para llegar al destino (que implicaba alejarse temporalmente del objetivo contorneando el obstáculo superior), la incapacidad de la estrategia de realizar *backtracking* (deshacer pasos y explorar ramificaciones alternativas) lo dejó atrapado en un "mínimo local". Esto demuestra la falta de completitud del algoritmo Greedy en laberintos o espacios con concavidades pronunciadas.

## 4. Conclusión
La estrategia Greedy resulta extremadamente rápida y eficiente computacionalmente, ya que no mantiene una frontera de exploración compleja ni evalúa múltiples rutas (como lo harían algoritmos tipo A* o Dijkstra). Sin embargo, su confiabilidad depende exclusivamente de la estructura del entorno. En entornos sin mínimos locales o con obstáculos convexos simples, es útil; pero en entornos complejos con obstáculos cóncavos, es altamente propenso a generar rutas ineficientes o quedar completamente atascado sin alcanzar una solución existente.
