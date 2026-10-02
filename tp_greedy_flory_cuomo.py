import json
import os

def cargar_mapa(ruta_archivo):
    with open(ruta_archivo, 'r') as f:
        return json.load(f)

# ==========================================
# ESTRUCTURA FORMAL DEL ALGORITMO GREEDY
# ==========================================

def funcion_objetivo(candidato, destino):
    """
    Define el resultado buscado (minimizar la distancia Manhattan).
    """
    return abs(candidato[0] - destino[0]) + abs(candidato[1] - destino[1])

def funcion_factibilidad(candidato, grilla, visitados):
    """
    Evalúa si un candidato es factible de formar parte de la solución.
    Verifica límites del mapa, obstáculos, zonas prohibidas y celdas visitadas.
    """
    filas = len(grilla)
    cols = len(grilla[0]) if filas > 0 else 0
    f, c = candidato
    
    # 1. Dentro de los límites
    if not (0 <= f < filas and 0 <= c < cols):
        return False
    # 2. Celda libre (0 = transitable)
    if grilla[f][c] != 0:
        return False
    # 3. No visitada anteriormente (Greedy no revisa decisiones)
    if candidato in visitados:
        return False
        
    return True

def funcion_seleccion(candidatos_factibles, destino):
    """
    Selecciona al mejor candidato (el que minimiza la función objetivo).
    El criterio de desempate se respeta por el orden en que se generan
    los candidatos (ARRIBA, DERECHA, ABAJO, IZQUIERDA).
    """
    mejor_candidato = None
    menor_distancia = float('inf')
    
    for candidato in candidatos_factibles:
        distancia = funcion_objetivo(candidato, destino)
        
        # Se requiere estricto menor (<) para preservar el orden inicial en empates
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_candidato = candidato
            
    return mejor_candidato

def funcion_solucion(ruta, destino):
    """
    Evalúa si el conjunto solución propuesto conforma la solución final.
    """
    if not ruta:
        return False
    return ruta[-1] == destino

def greedy_navegacion(datos_mapa):
    """
    Esquema general del algoritmo Greedy.
    """
    grilla = datos_mapa['grilla']
    inicio = tuple(datos_mapa['inicio'])
    destino = tuple(datos_mapa['destino'])
    max_pasos = datos_mapa['maximo_pasos']
    
    # Inicialización del conjunto solución
    ruta = [inicio]
    visitados = {inicio}
    pasos = 0
    
    # Orden estricto de generación: ARRIBA, DERECHA, ABAJO, IZQUIERDA
    direcciones = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    while not funcion_solucion(ruta, destino) and pasos < max_pasos:
        actual = ruta[-1]
        
        # Generamos todos los candidatos posibles desde la posición actual
        candidatos = [(actual[0] + df, actual[1] + dc) for df, dc in direcciones]
        
        # Filtramos mediante la función de factibilidad
        candidatos_factibles = [c for c in candidatos if funcion_factibilidad(c, grilla, visitados)]
        
        # Condición de bloqueo: no hay candidatos factibles
        if not candidatos_factibles:
            return "BLOQUEADO", ruta, pasos
            
        # Elegimos el mejor candidato
        mejor_candidato = funcion_seleccion(candidatos_factibles, destino)
        
        # Unión al conjunto solución
        ruta.append(mejor_candidato)
        visitados.add(mejor_candidato)
        pasos += 1
        
    # Verificación final
    if funcion_solucion(ruta, destino):
        return "DESTINO_ALCANZADO", ruta, pasos
    else:
        return "LIMITE_DE_PASOS", ruta, pasos

# ==========================================
# UTILIDADES Y TRADUCCION
# ==========================================

def traducir_ruta(ruta, orientacion_inicial, tamano_celda):
    direcciones = {"NORTE": 0, "ESTE": 1, "SUR": 2, "OESTE": 3}
    actual_dir = direcciones.get(orientacion_inicial.upper(), 1)
    
    instrucciones = []
    
    for i in range(len(ruta) - 1):
        actual = ruta[i]
        siguiente = ruta[i+1]
        
        df = siguiente[0] - actual[0]
        dc = siguiente[1] - actual[1]
        
        if df == -1 and dc == 0: nueva_dir = 0 # NORTE
        elif df == 0 and dc == 1: nueva_dir = 1 # ESTE
        elif df == 1 and dc == 0: nueva_dir = 2 # SUR
        elif df == 0 and dc == -1: nueva_dir = 3 # OESTE
        else: continue
            
        diff = (nueva_dir - actual_dir) % 4
        if diff == 1: instrucciones.append("GIRAR DERECHA 90°")
        elif diff == 2: instrucciones.append("GIRAR 180°")
        elif diff == 3: instrucciones.append("GIRAR IZQUIERDA 90°")
            
        instrucciones.append(f"AVANZAR {tamano_celda:.2f} m".replace('.', ','))
        actual_dir = nueva_dir
        
    return instrucciones

def imprimir_mapa(grilla, ruta, inicio, destino):
    filas = len(grilla)
    cols = len(grilla[0])
    
    print("\nMapa de navegación:")
    print("Leyenda: I=Inicio | D=Destino | *=Ruta | X=Obstáculo/Prohibido | .=Libre")
    for f in range(filas):
        fila_str = ""
        for c in range(cols):
            pos = (f, c)
            if pos == tuple(inicio):
                fila_str += "I "
            elif pos == tuple(destino):
                fila_str += "D "
            elif pos in ruta:
                fila_str += "* "
            elif grilla[f][c] in [1, 2]:
                fila_str += "X "
            else:
                fila_str += ". "
        print(fila_str)

def ejecutar_pruebas():
    archivos = ["mapas/mapa_1.json", "mapas/mapa_2.json", "mapas/mapa_3.json"]
    
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"No se encontró el archivo: {archivo}")
            continue
            
        datos = cargar_mapa(archivo)
        print("\n" + "="*70)
        print(f"Ejecutando: {datos['nombre']}")
        print("="*70)
        
        estado, ruta, pasos = greedy_navegacion(datos)
        
        print(f"Estado Final      : {estado}")
        print(f"Pasos realizados  : {pasos}")
        print(f"Ruta completa     : {ruta}")
        
        imprimir_mapa(datos['grilla'], ruta, datos['inicio'], datos['destino'])
        
        instrucciones = traducir_ruta(ruta, datos['orientacion_inicial'], datos['tamano_celda_metros'])
        print("\nSecuencia de instrucciones para el robot:")
        if instrucciones:
            print(" -> ".join(instrucciones))
        else:
            print("Ninguna (no hubo desplazamiento válido)")

if __name__ == '__main__':
    ejecutar_pruebas()
