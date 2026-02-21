#!/usr/bin/env python3
"""
10 - ASYNC/AWAIT BÁSICO
========================
asyncio: concurrencia con una sola hebra. async def, await, event loop.
Ideal para I/O-bound (red, disco). No bloquea el hilo en esperas.
Solo biblioteca estándar: asyncio. Python 3.10+
"""

import asyncio
import time


# ---------------------------------------------------------------------------
# Coroutine: función async; await solo dentro de async.
# ---------------------------------------------------------------------------

async def tarea_io(nombre: str, segundos: float):
    """Simula I/O: await asyncio.sleep no bloquea el event loop."""
    print(f"  [{nombre}] empiezo, espero {segundos}s")
    await asyncio.sleep(segundos)
    print(f"  [{nombre}] listo")
    return f"resultado-{nombre}"


def ejemplo_coroutine_simple():
    """asyncio.run() crea el event loop, ejecuta la coroutine, cierra el loop."""
    print("=== Coroutine simple ===")
    resultado = asyncio.run(tarea_io("A", 3.0))
    print(f"  Retorno: {resultado}")


# ---------------------------------------------------------------------------
# Varias tareas en paralelo: create_task() + await.
# ---------------------------------------------------------------------------

async def ejemplo_varias_tareas():
    """create_task() programa la coroutine; await recoge el resultado."""
    print("\n=== Varias tareas (create_task) ===")
    t1 = asyncio.create_task(tarea_io("T1", 10.0))
    t2 = asyncio.create_task(tarea_io("T2", 0.5))
    t3 = asyncio.create_task(tarea_io("T3", 2.0))
    # Las tres corren "a la vez"; el loop alterna cuando hacen await.
    
    # read from terminal and wait for user input
    #input("Press Enter to continue...")

    r1 = await t1
    print(f"  Resultado 1: {r1}")
    r2 = await t2
    print(f"  Resultado 2: {r2}")
    r3 = await t3
    print(f"  Resultado 3: {r3}")
    print(f"  Resultados: {r1}, {r2}, {r3}")


# ---------------------------------------------------------------------------
# asyncio.gather(): esperar varias coroutines y obtener lista de resultados.
# ---------------------------------------------------------------------------

async def ejemplo_gather():
    """gather() lanza todas y espera a que terminen; devuelve lista en orden."""
    print("\n=== asyncio.gather() ===")
    resultados = await asyncio.gather(
        tarea_io("G1", 3.3),
        tarea_io("G2", 5.1),
        tarea_io("G3", 1.2),
    )
    print(f"  Resultados: {resultados}")


# ---------------------------------------------------------------------------
# Secuencial vs concurrente: mismo trabajo, menos tiempo total con async.
# ---------------------------------------------------------------------------

async def trabajo_io(ident: int):
    await asyncio.sleep(2.0)
    return ident

async def tres_tareas_concurrentes():
    """Tres sleeps de 0.2s en paralelo ≈ 0.2s total (no 0.6s)."""
    print("\n=== Secuencial vs concurrente ===")
    inicio = time.perf_counter()
    r = await asyncio.gather(trabajo_io(1), trabajo_io(2), trabajo_io(3))
    duracion = time.perf_counter() - inicio
    print(f"  Tres tareas (0.2s cada una) en paralelo: {duracion:.2f}s (≈0.2s)")
    print(f"  Resultados: {r}")


def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    #hello_world()
    #ejemplo_coroutine_simple()
    #asyncio.run(ejemplo_varias_tareas())
    #asyncio.run(ejemplo_gather())
    asyncio.run(tres_tareas_concurrentes())
    print("\n--- Fin 10_async_basico ---")
