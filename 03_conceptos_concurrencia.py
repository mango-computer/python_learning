#!/usr/bin/env python3
"""
03 - CONCEPTOS: CONCURRENCIA Y PARALELISMO
==========================================
- Concurrencia: varias tareas "en progreso" (pueden alternarse en una CPU).
- Paralelismo: varias tareas ejecutándose a la vez (varias CPUs/núcleos).
- GIL (Global Interpreter Lock): en CPython solo un thread ejecuta bytecode a la vez.
  Por eso threads no dan paralelismo de CPU puro, pero sí concurrencia (I/O, etc.).
Solo biblioteca estándar. Python 3.10+
"""

import sys


def que_es_gil():
    """
    En CPython, el GIL hace que en un mismo proceso solo un thread ejecute
    bytecode Python a la vez. Por tanto:
    - Threads: buena opción para I/O (red, disco, esperas).
    - Procesos (multiprocessing): buena opción para CPU intensivo (cálculos).
    """
    print("=== GIL y consecuencias ===")
    print("Implementación:", sys.implementation.name)
    print("En CPython, múltiples threads comparten una sola ejecución de bytecode a la vez.")
    print("Usa multiprocessing para trabajo CPU-bound paralelo real.")


def cuando_threads_cuando_procesos():
    """Resumen práctico."""
    print("\n=== Cuándo usar qué ===")
    print("""
  THREADS (threading / ThreadPoolExecutor):
    - I/O bound: redes, disco, APIs, esperas.
    - Comparten memoria (fácil compartir datos, pero hay que sincronizar).
    - Menor overhead que procesos.

  PROCESOS (multiprocessing / ProcessPoolExecutor):
    - CPU bound: cálculos pesados, procesamiento de datos.
    - Sin GIL entre procesos: paralelismo real.
    - Memoria separada (comunicación por Queue, Pipe, etc.).
    """)


def concepto_race_condition():
    """
    Varios threads leyendo/escribiendo el mismo dato sin sincronización
    puede dar resultados incorrectos (race condition).
    En el siguiente módulo verás Lock y otros mecanismos.
    """
    print("\n=== Race condition (concepto) ===")
    print("Si dos threads hacen 'n = n + 1' sobre la misma variable,")
    print("el resultado puede ser incorrecto sin Lock. Ver 05_sincronizacion.")


if __name__ == "__main__":
    que_es_gil()
    cuando_threads_cuando_procesos()
    concepto_race_condition()
    print("\n--- Fin 03_conceptos_concurrencia ---")
