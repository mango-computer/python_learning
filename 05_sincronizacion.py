#!/usr/bin/env python3
"""
05 - SINCRONIZACIÓN ENTRE THREADS
=================================
Objetos nativos: Lock, RLock, Event, Condition, Semaphore.
Evitan race conditions y permiten coordinar hilos.
Solo biblioteca estándar: threading. Python 3.10+
"""

import threading
import time


# ---------------------------------------------------------------------------
# LOCK: exclusión mutua. Solo un thread puede tener el lock a la vez.
# ---------------------------------------------------------------------------

contador_compartido = 0
lock_contador = threading.Lock()


def incrementar_con_lock(veces: int):
    global contador_compartido
    for _ in range(veces):
        lock_contador.acquire()
        try:
            contador_compartido += 1
        finally:
            lock_contador.release()


def ejemplo_lock():
    """Sin lock, dos threads incrementando dan resultado incorrecto. Con lock, correcto."""
    global contador_compartido
    print("=== Lock (exclusión mutua) ===")
    contador_compartido = 0
    t1 = threading.Thread(target=incrementar_con_lock, args=(100_000_000,))
    t2 = threading.Thread(target=incrementar_con_lock, args=(100_000_000,))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Contador esperado 200000, obtenido: {contador_compartido}")

    # Forma preferida: with lock (libera automáticamente)
    print("\n=== Lock con 'with' ===")
    contador_compartido = 0

    def incrementar_with():
        global contador_compartido
        for _ in range(100_000):
            with lock_contador:
                contador_compartido += 1

    t1 = threading.Thread(target=incrementar_with)
    t2 = threading.Thread(target=incrementar_with)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print(f"Contador: {contador_compartido}")


# ---------------------------------------------------------------------------
# EVENT: un thread señala; otros esperan hasta que se señale.
# ---------------------------------------------------------------------------

def ejemplo_event():
    """Un thread espera un evento; otro lo dispara."""
    print("\n=== Event ===")
    listo = threading.Event()

    def esperar_evento():
        print("  [esperador] Esperando señal...")
        listo.wait()  # bloquea hasta que otro hilo llame listo.set()
        print("  [esperador] ¡Señal recibida!")

    def disparar_evento():
        time.sleep(5.0)
        print("  [disparador] Enviando señal")
        listo.set()

    t1 = threading.Thread(target=esperar_evento)
    t2 = threading.Thread(target=disparar_evento)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


# ---------------------------------------------------------------------------
# CONDITION: esperar hasta que se cumpla una condición (con Lock interno).
# ---------------------------------------------------------------------------

def ejemplo_condition():
    """Condition: wait() y notify() para coordinar con una condición."""
    print("\n=== Condition ===")
    cond = threading.Condition()
    dato = None

    def productor():
        nonlocal dato
        time.sleep(3.0)
        with cond:
            dato = "mensaje"
            cond.notify()  # despierta a uno que esté en wait()

    def consumidor():
        nonlocal dato
        with cond:
            while dato is None:
                cond.wait()  # suelta el lock y espera; al despertar lo re-adquiere
            print(f"  [consumidor] Recibí: {dato}")

    t1 = threading.Thread(target=consumidor)
    t2 = threading.Thread(target=productor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


# ---------------------------------------------------------------------------
# SEMAPHORE: límite de N threads en una sección a la vez.
# ---------------------------------------------------------------------------

def ejemplo_semaphore():
    """Semaphore(2): como máximo 2 threads ejecutando la sección a la vez."""
    print("\n=== Semaphore ===")
    sem = threading.Semaphore(2)

    def tarea(id_thread: int):
        with sem:
            print(f"  [thread {id_thread}] Dentro (solo 2 a la vez)")
            time.sleep(2.0)
        print(f"  [thread {id_thread}] Fuera")

    hilos = [threading.Thread(target=tarea, args=(i,)) for i in range(10)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()


if __name__ == "__main__":
    #ejemplo_lock()
    #ejemplo_event()
    #ejemplo_condition()
    ejemplo_semaphore()
    print("\n--- Fin 05_sincronizacion ---")
