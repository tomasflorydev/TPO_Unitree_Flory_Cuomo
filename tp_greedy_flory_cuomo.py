# carga de datos para greedy:

import json
import os

def cargar_mapa(ruta_archivo):
    # lee archivo json para obtener la grilla, inicio, destino, tamaño y orientacion
    with open(ruta_archivo, 'r') as f:
        return json.load(f)

# ALGORITMO GREEDY

def funcion_objetivo(candidato, destino):
    """
    define el resultado buscado (minimizar la distancia manhattan) = "mejor candidato"
    """
    # formula de distancia: abs(fila - filaDestino) + abs(columna - columnaDestino)
    return abs(candidato[0] - destino[0]) + abs(candidato[1] - destino[1])

def funcion_factibilidad(candidato, grilla, visitados):
    """
    evalua si un candidato es factible de formar parte de la solución.
    verifica límites del mapa, obstáculos, zonas prohibidas y celdas visitadas.
    filtra los movimientos que no son válidos para el robot.
    """
    filas = len(grilla)
    cols = len(grilla[0]) if filas > 0 else 0
    f, c = candidato
    
    # 1. verifica que la celda candidata no exceda los límites de la matriz (que quede fuera de la grilla)
    if not (0 <= f < filas and 0 <= c < cols):
        return False
    # 2. asegura que la celda sea transitable (0 representa una celda libre)
    # descarta valores 1 (obstáculo) y 2 (zona prohibida)
    if grilla[f][c] != 0:
        return False
    # 3. descarta celdas ya visitadas (Greedy no puede volver a decisiones anteriores)
    if candidato in visitados:
        return False
        
    return True

def funcion_seleccion(candidatos_factibles, destino):
    """
    selecciona al mejor candidato (el que minimiza la función objetivo).
    el criterio de desempate se respeta por el orden en que se generan
    los candidatos (arriba, derecha, abajo, izquierda)
    """
    mejor_candidato = None
    menor_distancia = float('inf')
    # ierta sobre los candidatos factibles
    for candidato in candidatos_factibles:
        distancia = funcion_objetivo(candidato, destino)
        
        # se usa < porque queremos el menor valor de distancia (minimizar)
        # si dos caminos tienen la misma distancia, se mantiene el orden (arriba, derecha, abajo, izquierda)
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_candidato = candidato
            
    return mejor_candidato

def funcion_solucion(ruta, destino):
    """
    evalua lo propuesto conforma la solución final: el ultimo paso coincide con
    las coordenadas de destino
    """
    if not ruta:
        return False
    return ruta[-1] == destino

def greedy_navegacion(datos_mapa):
    """
    aplicacion del algoritmo greedy completo
    """
    grilla = datos_mapa['grilla']
    inicio = tuple(datos_mapa['inicio'])
    destino = tuple(datos_mapa['destino'])
    max_pasos = datos_mapa['maximo_pasos']
    
    # inicializacion del conjunto solucion:
    ruta = [inicio]
    visitados = {inicio}
    pasos = 0

    # conjunto de movimientos posibles en el orden de desempate
    # (-1, 0) = arriba, (0, 1) = derecha, (1, 0) = abajo, (0, -1) = izquierda.
    direcciones = [(-1, 0), (0, 1), (1, 0), (0, -1)]

    # mientras que no se alcance el destino y no se supere el maximo de pasos:
    while not funcion_solucion(ruta, destino) and pasos < max_pasos:
        actual = ruta[-1]
        
        # genera todas las direcciones posibles desde la ubicacion actual (arriba, derecha, abajo, izquierda)
        candidatos = [(actual[0] + df, actual[1] + dc) for df, dc in direcciones]
        
        # funcion de factibilidad: descarta los candidatos que no son validos (fuera de limites de la grilla, obstaculos, prohibidos o visitados)
        candidatos_factibles = [c for c in candidatos if funcion_factibilidad(c, grilla, visitados)]

        # condicion de bloqueo: no hay candidatos factibles (lista de factibles vacia) - mapa 3
        if not candidatos_factibles:
            return "BLOQUEADO", ruta, pasos
            
        # elegir al mejor candidato: menor distancia a manhattan (funcion objetivo)
        mejor_candidato = funcion_seleccion(candidatos_factibles, destino)
        
        # actualiza el estado de la ruta y marca la celda como visitada
        ruta.append(mejor_candidato)
        visitados.add(mejor_candidato)
        pasos += 1
        
    # verificacion final:
    if funcion_solucion(ruta, destino):
        return "DESTINO_ALCANZADO", ruta, pasos # el robot llego a la celda de destino
    else:
        return "LIMITE_DE_PASOS", ruta, pasos # se alcanzo el maximo de pasos permitido


# traduccion de la ruta: convertir las coordenadas de la matriz en instrucciones de movimiento para el robot 
def traducir_ruta(ruta, orientacion_inicial, tamano_celda):
    '''
    mapea las direcciones en un sistema numerico:
    0 = NORTE, 1 = ESTE, 2 = SUR, 3 = OESTE
    '''
    direcciones = {"NORTE": 0, "ESTE": 1, "SUR": 2, "OESTE": 3}
    actual_dir = direcciones.get(orientacion_inicial.upper(), 1)
    
    instrucciones = []
    
    for i in range(len(ruta) - 1):
        actual = ruta[i]
        siguiente = ruta[i+1]

        # vector de desplazamiento entre la celda actual y la siguiente
        df = siguiente[0] - actual[0]
        dc = siguiente[1] - actual[1]

        # orientacion para un nuevo paso
        if df == -1 and dc == 0: nueva_dir = 0 # norte
        elif df == 0 and dc == 1: nueva_dir = 1 # este
        elif df == 1 and dc == 0: nueva_dir = 2 # sur
        elif df == 0 and dc == -1: nueva_dir = 3 # oeste
        else: continue

        # determina el giro necesario para alinear la orientacion actual con la nueva direccion (usando modulo 4)
        diff = (nueva_dir - actual_dir) % 4
        # traduce la ruta a instrucciones de orientacion para el robot
        if diff == 1: instrucciones.append("GIRAR DERECHA 90°")
        elif diff == 2: instrucciones.append("GIRAR 180°")
        elif diff == 3: instrucciones.append("GIRAR IZQUIERDA 90°")

        # transforma el desplazamiento en instrucciones, considerando el tamaño de cada celda en metros
        instrucciones.append(f"AVANZAR {tamano_celda:.2f} m".replace('.', ','))
        actual_dir = nueva_dir
        
    return instrucciones

# representacion visual de la grilla, la ruta y los puntos de inicio y destino
def imprimir_mapa(grilla, ruta, inicio, destino):
    # dimensiones de la matriz
    filas = len(grilla)
    cols = len(grilla[0])
    
    print("\nMapa de navegacion:")
    print("I=inicio | D=destino | *=Ruta | X=obstaculo/prohibido | .=libre")
    # recorrer cada celda de la matriz
    for f in range(filas):
        fila_str = ""
        for c in range(cols):
            pos = (f, c)
            # marca cada celda con lo que es, segun el mapa de navegacion
            if pos == tuple(inicio):
                fila_str += "I "
            elif pos == tuple(destino):
                fila_str += "D "
            elif pos in ruta:
                fila_str += "* "
            elif grilla[f][c] in [1, 2]: # zonas bloqueadas - 1 = obstaculo, 2 = zona prohibida
                fila_str += "X "
            else:
                fila_str += ". "
        # imprime la fila completa antes de saltar a la siguiente, construyendo la grilla
        print(fila_str)

# casos de prueba: ejecutar greedy con los mapas y mostrar los resultados
def ejecutar_pruebas():
    archivos = ["mapas/mapa_1.json", "mapas/mapa_2.json", "mapas/mapa_3.json"]
    
    for archivo in archivos:
        # que el programa no falle si algun archivo no existe, que continue con los demas mapas
        if not os.path.exists(archivo):
            print(f"No se encontró el archivo: {archivo}")
            continue

        # carga de datos y grilla
        datos = cargar_mapa(archivo)
        print("\n" + "="*70)
        print(f"Ejecutando: {datos['nombre']}")
        print("="*70)

        # devuelve la ruta calculada, el estado final y la cantidad de pasos realizados
        estado, ruta, pasos = greedy_navegacion(datos)

        # muestra los estados posibles: DESTINO_ALCANZADO, BLOQUEADO, o LIMITE_DE_PASOS
        print(f"Estado Final: {estado}")
        print(f"Pasos realizados: {pasos}")
        print(f"Ruta completa: {ruta}")

        imprimir_mapa(datos['grilla'], ruta, datos['inicio'], datos['destino'])

        # genera la secuencia de instrucciones para el robot
        instrucciones = traducir_ruta(ruta, datos['orientacion_inicial'], datos['tamano_celda_metros'])
        print("\nSecuencia de instrucciones para el robot:")
        if instrucciones:
            # concatena la lista de strings con una flecha para una lectura mas clara
            print(" -> ".join(instrucciones))
        else:
            print("Ninguna (no hubo desplazamiento valido)")

if __name__ == '__main__':
    ejecutar_pruebas()
