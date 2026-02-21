#!/usr/bin/env python3
"""
11 - ASYNC/AWAIT MEDIUM
========================
Timeouts, Lock, Queue, manejo de errores en asyncio.
Solo biblioteca estándar: asyncio. Python 3.10+
"""

import asyncio
import time


# ---------------------------------------------------------------------------
# Timeout: asyncio.wait_for(coro, timeout=...) lanza asyncio.TimeoutError.
# ---------------------------------------------------------------------------

async def tarea_lenta(segundos: float):
    try:
        await asyncio.sleep(segundos)
        print("  Tarea completada")
        return "ok"
    except asyncio.TimeoutError:
        print("  Timeout: la tarea no terminó en 2.5s.")
        raise asyncio.TimeoutError

    except asyncio.CancelledError:
        print("  Tarea cancelada")
        raise asyncio.CancelledError

    finally:
        print("  Tarea finalizada")
        print("  Liberando recursos")
        return "error"


async def ejemplo_timeout():
    """wait_for() cancela la tarea si supera el tiempo."""
    print("=== Timeout con wait_for() ===")
    try:
        r = await asyncio.wait_for(tarea_lenta(5.0), timeout=2.5)
        print(f"  Resultado: {r}")
    except asyncio.TimeoutError:
        print("  Timeout: la tarea no terminó en 2.5s.")


# ---------------------------------------------------------------------------
# asyncio.Lock: exclusión mutua entre coroutines (una a la vez en la sección).
# ---------------------------------------------------------------------------

contador = 0
lock = asyncio.Lock()

async def incrementar_con_lock(veces: int, name: str):
    global contador
    for _ in range(veces):
        async with lock:
            contador += 1
            print(f"  [lock] {name} incrementó contador a {contador}")

async def ejemplo_async_lock():
    """Lock evita race condition cuando varias coroutines modifican estado compartido."""
    global contador
    print("\n=== asyncio.Lock ===")
    contador = 0
    await asyncio.gather(
        incrementar_con_lock(10_000, "A"),
        incrementar_con_lock(10_000, "B"),
    )
    print(f"  Contador esperado 20000, obtenido: {contador}")


# ---------------------------------------------------------------------------
# asyncio.Queue: cola async; put/get son coroutines, no bloquean el loop.
# ---------------------------------------------------------------------------

async def productor_async(cola: asyncio.Queue, n: int):
    for i in range(n):
        await cola.put(f"item-{i}")
        print(f"  [productor] put item-{i}")
    await cola.put(None)  # señal de fin

async def consumidor_async(cola: asyncio.Queue):
    while True:
        item = await cola.get()
        if item is None:
            break
        print(f"  [consumidor] get {item}")
    print("  [consumidor] fin")

async def ejemplo_async_queue():
    """Producer-consumer con asyncio.Queue (put/get son await)."""
    print("\n=== asyncio.Queue ===")
    cola = asyncio.Queue()
    await asyncio.gather(
        productor_async(cola, 3),
        consumidor_async(cola),
    )


# ---------------------------------------------------------------------------
# Errores en gather: return_exceptions=True para no cancelar el resto.
# ---------------------------------------------------------------------------

async def tarea_ok(x: int):
    await asyncio.sleep(0.05)
    return x

async def tarea_falla():
    await asyncio.sleep(0.05)
    raise ValueError("error en coroutine")

async def ejemplo_gather_exceptions():
    """gather(..., return_exceptions=True) devuelve resultados o excepciones."""
    print("\n=== gather con return_exceptions ===")
    resultados = await asyncio.gather(
        tarea_ok(1),
        tarea_falla(),
        tarea_ok(2),
        return_exceptions=True,
    )
    for i, r in enumerate(resultados):
        if isinstance(r, Exception):
            print(f"  Tarea {i}: excepción {r!r}")
        else:
            print(f"  Tarea {i}: {r}")


# ---------------------------------------------------------------------------
# Semaphore: límite de N coroutines en una sección a la vez.
# ---------------------------------------------------------------------------

async def tarea_con_sem(sem: asyncio.Semaphore, id_: int):
    async with sem:
        print(f"  [sem] {id_} dentro (máx 2 a la vez)")
        await asyncio.sleep(0.3)
    print(f"  [sem] {id_} fuera")

async def ejemplo_semaphore():
    """Semaphore(2): como máximo 2 coroutines ejecutando la sección."""
    print("\n=== asyncio.Semaphore ===")
    sem = asyncio.Semaphore(2)
    await asyncio.gather(*(tarea_con_sem(sem, i) for i in range(4)))


async def print_something(something: str, delay: float, times: int):
    for _ in range(times):
        print(something)
        await asyncio.sleep(delay)
    print(f"Finished printing {something} {times} times")


async def main():
    await asyncio.gather(
        print_something("Hello", 1, 10),
        print_something("World", 2, 5),
    )


if __name__ == "__main__":
    

    #asyncio.run(main())
    #asyncio.run(ejemplo_timeout())
    asyncio.run(ejemplo_async_lock())
    #asyncio.run(ejemplo_async_queue())
    #asyncio.run(ejemplo_gather_exceptions())
    #asyncio.run(ejemplo_semaphore())
    print("\n--- Fin 11_async_medium ---")
