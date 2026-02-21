#!/usr/bin/env python3
"""
09 - PRÁCTICA INTEGRADA
=======================
Ejemplo que combina: threads, queue.Queue (comunicación), Lock (sincronización)
y un loop principal que orquesta productores y consumidores.
Solo biblioteca estándar. Python 3.10+
"""

import queue
import threading
import time


def practica_producer_consumer_con_lock():
    """
    Varios productores ponen trabajo en una cola; varios consumidores sacan y procesan.
    Un Lock protege un contador compartido de tareas completadas.
    """
    print("=== Producer-Consumer con Queue y Lock ===\n")
    cola = queue.Queue()
    lock_contador = threading.Lock()
    tareas_completadas = [0]  # lista para poder modificar desde nested function
    N_TAREAS = 6
    N_CONSUMIDORES = 2

    def productor(id_prod: int):
        for i in range(N_TAREAS // 2):  # 2 productores, 3 tareas cada uno
            item = f"P{id_prod}-{i}"
            cola.put(item)
            print(f"  [productor {id_prod}] puse {item}")
        print(f"  [productor {id_prod}] fin")

    def consumidor(id_cons: int):
        while True:
            try:
                item = cola.get(timeout=0.5)
            except queue.Empty:
                break
            print(f"  [consumidor {id_cons}] proceso {item}")
            time.sleep(0.1)
            with lock_contador:
                tareas_completadas[0] += 1
            cola.task_done()
        print(f"  [consumidor {id_cons}] fin")

    # Productores
    prod1 = threading.Thread(target=productor, args=(1,))
    prod2 = threading.Thread(target=productor, args=(2,))
    prod1.start()
    prod2.start()

    # Consumidores
    consumidores = [
        threading.Thread(target=consumidor, args=(i,))
        for i in range(N_CONSUMIDORES)
    ]
    for c in consumidores:
        c.start()

    prod1.join()
    prod2.join()
    for c in consumidores:
        c.join()

    print(f"\nTareas completadas (con Lock): {tareas_completadas[0]}")


def practica_evento_sincronizado():
    """Un thread espera un evento; otro lo dispara tras hacer algo."""
    print("\n=== Event: esperar señal ===\n")
    listo = threading.Event()
    resultado = []

    def trabajador():
        print("  [trabajador] Trabajando...")
        time.sleep(0.3)
        resultado.append("hecho")
        listo.set()
        print("  [trabajador] Señal enviada.")

    def coordinador():
        t = threading.Thread(target=trabajador)
        t.start()
        print("  [coordinador] Esperando señal...")
        listo.wait()
        print("  [coordinador] Recibida. Resultado:", resultado)
        t.join()

    coordinador()


if __name__ == "__main__":
    #practica_producer_consumer_con_lock()
    practica_evento_sincronizado()
    print("\n--- Fin 09_practica_integrada ---")
