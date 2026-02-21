#!/usr/bin/env python3
"""
04 - THREADING BÁSICO
=====================
threading.Thread: crear un hilo que ejecuta una función.
start() inicia la ejecución; join() espera a que termine.
Solo biblioteca estándar: threading. Python 3.10+
"""

import threading
import time


def tarea_simple():
    """Función que se ejecutará en un hilo."""
    print("  [thread] Hola desde el hilo")
    time.sleep(0.2)
    print("  [thread] Terminé")


def ejemplo_crear_un_thread():
    """Crear un thread, iniciarlo y esperar con join()."""
    print("=== Un solo thread ===")
    print("[main] Creando thread...")
    hilo = threading.Thread(target=tarea_simple)
    hilo.start()  # inicia la ejecución en paralelo
    print("[main] Esperando al thread con join()...")
    hilo.join()   # el main espera a que el hilo termine
    print("[main] Thread terminado.")


def tarea_con_nombre(nombre: str, segundos: float = 0.3):
    """Función con argumentos (args/kwargs se pasan al crear el Thread)."""
    print(f"  [thread {nombre}] Inicio, duermo {segundos}s")
    time.sleep(segundos)
    print(f"  [thread {nombre}] Fin")


def ejemplo_args_kwargs():
    """Pasar argumentos al thread con args= y kwargs=."""
    print("\n=== Thread con argumentos ===")
    h = threading.Thread(target=tarea_con_nombre, args=("A",), kwargs={"segundos": 0.2})
    h.start()
    h.join()
    print("[main] Listo.")


def ejemplo_varios_threads():
    """Varios threads ejecutándose concurrentemente."""
    print("\n=== Varios threads ===")
    hilos = []
    for i in range(3):
        h = threading.Thread(target=tarea_con_nombre, args=(f"T{i}", 5.0))
        hilos.append(h)
        h.start()
    for h in hilos:
        h.join()
    print("[main] Todos terminaron.")


def ejemplo_daemon():
    """
    Daemon threads: se terminan cuando el programa principal termina.
    No hace falta hacer join() de ellos (el proceso no espera).
    Útil para tareas de fondo que no deben bloquear la salida.
    """
    print("\n=== Daemon thread ===")

    def tarea_infinita():
        while True:
            print("  [daemon] tick")
            time.sleep(0.5)

    d = threading.Thread(target=tarea_infinita, daemon=True)
    d.start()
    time.sleep(4.0)  # main sigue un poco
    print("[main] Salgo; el daemon se corta con el proceso.")
    # No hacemos join(); el proceso termina y el daemon muere


def ejemplo_thread_actual():
    """Obtener el thread actual y su nombre."""
    print("\n=== Thread actual ===")

    def mostrar_quien_soy():
        t = threading.current_thread()
        print(f"  Soy: {t.name}, daemon={t.daemon}")

    h = threading.Thread(target=mostrar_quien_soy, name="MiHilo")
    h.start()
    h.join()
    print(f"  Main es: {threading.main_thread().name}")
    mostrar_quien_soy()
    

if __name__ == "__main__":
    #ejemplo_crear_un_thread()
    #ejemplo_args_kwargs()
    #ejemplo_varios_threads()
    #ejemplo_daemon()
    ejemplo_thread_actual()
    print("\n--- Fin 04_threading_basico ---")
