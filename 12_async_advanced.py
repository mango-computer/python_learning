#!/usr/bin/env python3
"""
12 - ASYNC/AWAIT AVANZADO
==========================
run_in_executor (mezclar I/O async con trabajo CPU o bloqueante).
Producer-consumer con Queue, patrones de cancelación y cierre.
Solo biblioteca estándar: asyncio. Python 3.10+
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor


# ---------------------------------------------------------------------------
# run_in_executor: ejecutar código bloqueante sin bloquear el event loop.
# ---------------------------------------------------------------------------

# En lugar de:
#loop = asyncio.get_running_loop()
#resultado = await loop.run_in_executor(None, trabajo_cpu, 100)

# Puedes escribir:
#resultado = await asyncio.to_thread(trabajo_cpu, 100)

def trabajo_cpu(n: int) -> int:
    """Función bloqueante (CPU o I/O síncrono). No usar await dentro."""
    time.sleep(5.0)  # simula CPU o I/O bloqueante (corto para ejemplos rápidos)
    return sum(range(n + 1))


def trabajo_cpu_corto(n: int, segundos: float = 2.0) -> int:
    """Bloqueante varios segundos; para demostrar bloqueo del event loop."""
    time.sleep(segundos)
    return sum(range(n + 1))


async def indicador_loop(duracion: float = 5.0, intervalo: float = 0.5):
    """Imprime '[loop] vivo' cada intervalo; demuestra si el event loop puede seguir."""
    inicio = time.perf_counter()
    while time.perf_counter() - inicio < duracion:
        print("  [loop] vivo")
        await asyncio.sleep(intervalo)


async def ejemplo_bloqueo_vs_executor():
    """Comparación: llamada directa BLOQUEA el loop; run_in_executor NO."""
    print("\n=== DEMO: ¿Se bloquea el event loop? ===\n")

    # --- Parte 1: llamada DIRECTA (bloqueante) ---
    async def tarea_llamada_directa():
        print("  [tarea] Llamando trabajo_cpu_corto(10, 20) DIRECTAMENTE (sin executor)...")
        r = trabajo_cpu_corto(10, 5.0)  # bloquea el hilo ~20 s
        print(f"  [tarea] Listo. Resultado: {r}")

    print("--- Con llamada DIRECTA: el indicador [loop] vivo se CONGELA ~2 s ---")
    await asyncio.gather(indicador_loop(10.0), tarea_llamada_directa())

    # --- Parte 2: run_in_executor (no bloqueante) ---
    loop = asyncio.get_running_loop()
    async def tarea_con_executor():
        print("\n  [tarea] Usando await run_in_executor(trabajo_cpu_corto, 10, 20)...")
        r = await loop.run_in_executor(None, trabajo_cpu_corto, 10, 5.0)
        print(f"  [tarea] Listo. Resultado: {r}")

    print("\n--- Con run_in_executor: el indicador [loop] vivo SIGUE imprimiendo ---")
    await asyncio.gather(indicador_loop(10.0), tarea_con_executor())
    print("\n  (Si viste '[loop] vivo' cada 0.5 s durante los 2 s, el loop no se bloqueó.)\n")


async def ejemplo_run_in_executor():
    """loop.run_in_executor() corre la función en un thread/process pool."""
    print("=== run_in_executor (ThreadPool por defecto) ===")
    loop = asyncio.get_running_loop()
    # Por defecto usa ThreadPoolExecutor del loop.
    resultado = await loop.run_in_executor(None, trabajo_cpu, 100)
    print(f"  sum(0..100) = {resultado}")

async def ejemplo_executor_explicito():
    """Puedes pasar tu propio ThreadPoolExecutor o ProcessPoolExecutor."""
    print("\n=== run_in_executor con executor propio ===")
    loop = asyncio.get_running_loop()
    inicio = time.perf_counter()
    with ThreadPoolExecutor(max_workers=2) as pool:
        # Así SÍ corren en paralelo (ambas tareas en el pool a la vez)
        r1_fut = loop.run_in_executor(pool, trabajo_cpu, 50)
        r2_fut = loop.run_in_executor(pool, trabajo_cpu, 100)
        r1, r2 = await asyncio.gather(r1_fut, r2_fut)    
    duracion = time.perf_counter() - inicio
    print(f"  Resultados: {r1}, {r2} en {duracion:.2f}s")


# ---------------------------------------------------------------------------
# Varias tareas con run_in_executor: trabajo "bloqueante" en paralelo.
# ---------------------------------------------------------------------------

async def ejemplo_varios_executor():
    """Varias llamadas run_in_executor se ejecutan en paralelo (varios threads)."""
    print("\n=== Varias tareas en executor ===")
    loop = asyncio.get_running_loop()
    inicio = time.perf_counter()
    resultados = await asyncio.gather(
        loop.run_in_executor(None, trabajo_cpu, 10),
        loop.run_in_executor(None, trabajo_cpu, 20),
        loop.run_in_executor(None, trabajo_cpu, 30),
    )
    duracion = time.perf_counter() - inicio
    print(f"  Tres tareas (0.1s cada una) en paralelo: {duracion:.2f}s")
    print(f"  Resultados: {resultados}")


# ---------------------------------------------------------------------------
# Producer-consumer con Queue y señal de cierre (varios consumidores).
# ---------------------------------------------------------------------------

async def productor(cola: asyncio.Queue, n: int):
    for i in range(n):
        await cola.put(("item", i))
    for _ in range(2):  # dos consumidores
        await cola.put((None, None))  # sentinela por consumidor

async def consumidor(cola: asyncio.Queue, id_: int):
    while True:
        tipo, valor = await cola.get()
        if tipo is None:
            cola.task_done()
            break
        print(f"  [C{id_}] procesó {tipo}-{valor}")
        cola.task_done()

async def ejemplo_producer_consumer_multi():
    """Un productor, dos consumidores, asyncio.Queue con task_done."""
    print("\n=== Producer-consumer (varios consumidores) ===")
    cola = asyncio.Queue()
    await asyncio.gather(
        productor(cola, 5),
        consumidor(cola, 1),
        consumidor(cola, 2),
    )


# ---------------------------------------------------------------------------
# Cancelación de tareas: Task.cancel() y manejo de CancelledError.
# ---------------------------------------------------------------------------

async def tarea_cancelable(segundos: float):
    try:
        await asyncio.sleep(segundos)
        return "terminé"
    except asyncio.CancelledError:
        print("  [tarea] cancelada")
        raise

async def ejemplo_cancelacion():
    """cancel() solicita cancelar la tarea; la tarea puede limpiar en CancelledError."""
    print("\n=== Cancelación de tareas ===")
    t = asyncio.create_task(tarea_cancelable(10.0))
    await asyncio.sleep(0.1)
    t.cancel()
    try:
        await t
    except asyncio.CancelledError:
        print("  Main: tarea fue cancelada.")


# ---------------------------------------------------------------------------
# asyncio.wait(): esperar con FIRST_COMPLETED, ALL_COMPLETED, etc.
# ---------------------------------------------------------------------------

async def tarea_con_id(ident: int, delay: float):
    await asyncio.sleep(delay)
    return ident

async def ejemplo_wait_first_completed():
    """wait(..., return_when=FIRST_COMPLETED) para el primero que termine."""
    print("\n=== asyncio.wait (FIRST_COMPLETED) ===")
    tareas = [asyncio.create_task(tarea_con_id(i, 0.1 * (i + 1))) for i in range(5)]
    done, pending = await asyncio.wait(tareas, return_when=asyncio.FIRST_COMPLETED)
    print(f"  Primera en terminar: {len(done)} tarea(s)")
    for t in done:
        print(f"    resultado: {t.result()}")
    # Cancelar el resto si ya no las necesitas
    for t in pending:
        t.cancel()
    await asyncio.gather(*pending, return_exceptions=True)


async def main():
    await ejemplo_bloqueo_vs_executor()
    await ejemplo_run_in_executor()
    await ejemplo_executor_explicito()
    await ejemplo_varios_executor()
    await ejemplo_producer_consumer_multi()
    await ejemplo_cancelacion()
    await ejemplo_wait_first_completed()


if __name__ == "__main__":
    asyncio.run(main())
    print("\n--- Fin 12_async_advanced ---")
