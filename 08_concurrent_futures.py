#!/usr/bin/env python3
"""
08 - CONCURRENT.FUTURES
=======================
API de alto nivel: ThreadPoolExecutor (threads) y ProcessPoolExecutor (procesos).
submit() devuelve un Future; map() aplica función a un iterable en paralelo.
Solo biblioteca estándar: concurrent.futures. Python 3.10+
"""

import concurrent.futures
import time


def tarea_lenta(x: int, duracion: float = 2.0) -> int:
    """Simula trabajo (I/O o CPU)."""
    time.sleep(duracion)
    return x * 2


def ejemplo_thread_pool_submit():
    """ThreadPoolExecutor: submit() devuelve Future; result() obtiene el resultado."""
    print("=== ThreadPoolExecutor con submit() ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(tarea_lenta, i) for i in range(5)]
        for f in concurrent.futures.as_completed(futures):
            print(f"  resultado: {f.result()}")


def ejemplo_thread_pool_map():
    """map() aplica la función a cada elemento; mantiene el orden de resultados."""
    print("\n=== ThreadPoolExecutor con map() ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        resultados = list(executor.map(tarea_lenta, range(5)))
    print("  resultados:", resultados)

def ejemplo_thread_pool_map_in_for():
    print("\n=== ThreadPoolExecutor con map() en for ===")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        for r in executor.map(tarea_lenta, range(5)):
            print(r)  # 0, 2, 4, 6, 8 (en ese orden)

def tarea_cpu(n: int) -> int:
    """Tarea CPU-bound: suma 1..n (para ProcessPoolExecutor)."""
    return sum(range(n + 1))


def ejemplo_process_pool():
    """ProcessPoolExecutor: mismo API, pero procesos (paralelismo real)."""
    print("\n=== ProcessPoolExecutor ===")
    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(tarea_cpu, 10_000) for _ in range(4)]
        for f in concurrent.futures.as_completed(futures):
            print(f"  resultado: {f.result()}")


def ejemplo_future_timeout():
    """result(timeout=...) lanza TimeoutError si tarda más."""
    print("\n=== Future con timeout ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(time.sleep, 2)
        try:
            f.result(timeout=3.5)
        except concurrent.futures.TimeoutError:
            print("  Timeout: la tarea no terminó a tiempo.")


def ejemplo_exception_en_future():
    """Si la función lanza, la excepción se propaga al llamar result()."""
    print("\n=== Excepción en Future ===")
    def falla():
        raise ValueError("error en el thread")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(falla)
        try:
            f.result()
        except ValueError as e:
            print(f"  Capturado: {e}")


if __name__ == "__main__":
    ejemplo_thread_pool_submit()
    ejemplo_thread_pool_map()
    ejemplo_thread_pool_map_in_for()
    ejemplo_process_pool()
    ejemplo_future_timeout()
    ejemplo_exception_en_future()
    print("\n--- Fin 08_concurrent_futures ---")
