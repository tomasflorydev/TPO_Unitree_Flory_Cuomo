import sys
import time
import math
from pathlib import Path

# Agregamos la ruta absoluta del repositorio del simulador al path de Python 
# para poder importar la API del robot G1 sin mover este archivo de lugar.
RUTA_SIMULADOR = Path("/Users/toms/Dev/UadeRobotLab/04Simuladores/UnitreeMujocoOficial")
sys.path.insert(0, str(RUTA_SIMULADOR))

try:
    from g1_student_api import RobotG1
except ImportError:
    print("❌ Error: No se pudo importar RobotG1.")
    print(f"Asegurate de que el repositorio de la cátedra esté en:\n{RUTA_SIMULADOR}")
    sys.exit(1)

# Importamos nuestro algoritmo Greedy y funciones auxiliares
from tp_greedy_flory_cuomo import cargar_mapa, greedy_navegacion, traducir_ruta

def ejecutar_ruta(robot: RobotG1, ruta_mapa: str):
    """
    Resuelve el mapa con nuestro código y transmite los comandos al simulador.
    """
    datos = cargar_mapa(ruta_mapa)
    print(f"\n{'='*50}")
    print(f"🤖 Ejecutando: {datos['nombre']} en Simulador G1")
    print(f"{'='*50}")
    
    estado, ruta, pasos = greedy_navegacion(datos)
    
    if estado == "BLOQUEADO":
        print("⚠️ El algoritmo resolvió el mapa y detectó BLOQUEO.")
        print("El robot no se moverá porque no hay ruta posible (Escenario 3).")
        return
        
    instrucciones = traducir_ruta(ruta, datos['orientacion_inicial'], datos['tamano_celda_metros'])
    print(f"✅ Ruta calculada exitosamente en {pasos} pasos.")
    print("Iniciando movimiento físico...\n")
    
    # Iteramos la ruta traducida y la convertimos en velocidades y tiempos para el G1
    for instruccion in instrucciones:
        print(f"▶️ Ejecutando: {instruccion}")
        
        if "AVANZAR" in instruccion:
            # Extraer los metros ("AVANZAR 0,50 m" -> 0.50)
            distancia_str = instruccion.split(" ")[1].replace(",", ".")
            distancia = float(distancia_str)
            
            # MRU: tiempo = distancia / velocidad
            velocidad = 0.25 # m/s
            tiempo = distancia / velocidad
            robot.movimiento(adelante=velocidad, costado=0.0, giro=0.0, tiempo=tiempo)
            
        elif "GIRAR DERECHA 90°" in instruccion:
            # Girar -90° (Hacia la derecha, sentido horario, radianes negativos)
            velocidad_angular = -0.5 # rad/s
            # tiempo = abs(radianes / velocidad_angular) -> pi/2 radianes
            tiempo = abs((math.pi / 2) / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        elif "GIRAR IZQUIERDA 90°" in instruccion:
            # Girar +90° (Hacia la izquierda, sentido antihorario, radianes positivos)
            velocidad_angular = 0.5 # rad/s
            tiempo = abs((math.pi / 2) / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        elif "GIRAR 180°" in instruccion:
            # Girar 180° (pi radianes)
            velocidad_angular = 0.5 # rad/s
            tiempo = abs(math.pi / velocidad_angular)
            robot.movimiento(adelante=0.0, costado=0.0, giro=velocidad_angular, tiempo=tiempo)
            
        # Pequeña pausa para estabilizar al robot entre comandos
        robot.detenerse()
        time.sleep(0.5)
        
    print("\n🏁 ¡Recorrido finalizado exitosamente!")
    robot.saludar()
    time.sleep(2)

def main():
    robot = RobotG1()
    print("⏳ Conectando al simulador MuJoCo...")
    robot.conectar()
    
    try:
        # Aquí puedes elegir qué mapa enviar al simulador:
        ejecutar_ruta(robot, "mapas/mapa_1.json")
        
        # Podes descomentar para probar los otros:
        # ejecutar_ruta(robot, "mapas/mapa_2.json")
        # ejecutar_ruta(robot, "mapas/mapa_3.json")
        
    except KeyboardInterrupt:
        print("\n🛑 Ejecución interrumpida por el usuario.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error: {e}")
    finally:
        robot.detenerse()
        robot.desconectar()
        print("🔌 Desconectado.")

if __name__ == "__main__":
    main()
