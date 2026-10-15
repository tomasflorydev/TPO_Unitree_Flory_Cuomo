

import sys
import time
import math
from pathlib import Path

# agregamos la ruta del repositorio del simulador para poder importar la API del robot.
RUTA_SIMULADOR = Path("/Users/toms/Dev/UadeRobotLab/04Simuladores/UnitreeMujocoOficial")
sys.path.insert(0, str(RUTA_SIMULADOR))

try:
    from g1_student_api import RobotG1
except ImportError:
    print("No se pudo importar RobotG1.")
    sys.exit(1)

from tp_greedy_flory_cuomo import cargar_mapa, greedy_navegacion, traducir_ruta

def ejecutar_ruta(robot: RobotG1, ruta_mapa: str):
    """
    resuelve el mapa y lo carga en el simulador.
    """
    datos = cargar_mapa(ruta_mapa)
    print(f" Ejecutando: {datos['nombre']}")
    
    estado, ruta, pasos = greedy_navegacion(datos)
    
    if estado == "BLOQUEADO":
        print("El algoritmo detecto bloqueo, no se hace el recorrido.")
        return
        
    instrucciones = traducir_ruta(ruta, datos['orientacion_inicial'], datos['tamano_celda_metros'])
    print(f"Ruta calculada en {pasos} pasos.")
    
    for instruccion in instrucciones:
        print(f" Ejecutando: {instruccion}")
        
        if "AVANZAR" in instruccion:
            # extraer los metros 
            distancia_str = instruccion.split(" ")[1].replace(",", ".")
            distancia = float(distancia_str)
            
            velocidad = 0.25 
            tiempo = distancia / velocidad
            robot.movimiento(adelante=velocidad, costado=0.0, giro=0.0, tiempo=tiempo)
            
        elif "GIRAR DERECHA 90°" in instruccion:
           
            velocidad_angular = -0.5 
            tiempo = abs((math.pi / 2) / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        elif "GIRAR IZQUIERDA 90°" in instruccion:
            velocidad_angular = 0.5 
            tiempo = abs((math.pi / 2) / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        elif "GIRAR 180°" in instruccion:
            velocidad_angular = 0.5 
            tiempo = abs(math.pi / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        # pausa
        robot.detenerse()
        time.sleep(0.5)
        
    print("\n Recorrido terminado")
    robot.saludar()
    time.sleep(2)

def main():
    robot = RobotG1()
    robot.conectar()
    
    try:
        ejecutar_ruta(robot, "mapas/mapa_1.json")
        
        # ejecutar_ruta(robot, "mapas/mapa_2.json")
        # ejecutar_ruta(robot, "mapas/mapa_3.json")
        
    except KeyboardInterrupt:
        print("Ejecución interrumpida.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        robot.detenerse()
        robot.desconectar()
        print(" Desconectado.")

if __name__ == "__main__":
    main()
