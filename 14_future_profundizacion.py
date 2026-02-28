#!/usr/bin/env python3
"""
14 - FUTURE: PROFUNDIZACIÓN
============================
Future = promesa de resultado futuro. Ejemplos en concurrent.futures y asyncio.
done(), result(), timeout, cancelación, as_completed(), wait().
asyncio.Future, Task (subclase), comparación. Solo biblioteca estándar. Python 3.10+
"""

import asyncio
import concurrent.futures
import time


# ---------------------------------------------------------------------------
# CONCURRENT.FUTURES.FUTURE: devuelto por executor.submit()
# ---------------------------------------------------------------------------

def tarea(ident: int, segundos: float = 0.2) -> int:
    print(f"Tarea {ident} iniciada")
    time.sleep(segundos)
    print(f"Tarea {ident} terminada")
    return ident * 10

def ejemplo_future_done_result():
    """
    done() indica si terminó; running() indica si está en ejecución; result() bloquea hasta tener el valor.
    running() indica si está en ejecución;
    cancelled() indica si fue cancelada; exception() devuelve la excepción si la tarea falló.
    add_done_callback(fn) llama a fn(future) cuando la tarea termina.
    """
    print("=== concurrent.futures.Future: done() y result() ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f = executor.submit(tarea, 1, 0.3)
        print(f"  Inmediatamente después de submit: done={f.done()}, running={f.running()}")
        time.sleep(0.35)
        print(f"  Tras 0.35s: done={f.done()}, running={f.running()}")
        r = f.result()
        print(f"  result() = {r}")
        print(f"  Tras result(): done={f.done()}, cancelled={f.cancelled()}, running={f.running()}")

def ejemplo_future_timeout():
    """result(timeout=X) lanza TimeoutError si no termina a tiempo."""
    print("\n=== Future.result(timeout=...) ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(time.sleep, 2.0)
        try:
            f.result(timeout=0.3)
        except concurrent.futures.TimeoutError:
            print("  TimeoutError: la tarea no terminó en 0.3s")
        # El thread sigue corriendo; al salir del with, shutdown(wait=True) espera

def ejemplo_future_exception():
    """Si la tarea lanza, result() re-lanza la excepción; exception() la devuelve."""
    print("\n=== Excepción en Future ===")
    def falla():
        raise RuntimeError("error en la tarea")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(falla)
        try:
            f.result()
        except RuntimeError as e:
            print(f"  result() propagó: {e}")
        # También puedes inspeccionar sin re-lanzar:
        exc = f.exception()
        print(f"  f.exception() = {exc}")

def ejemplo_as_completed():
    """as_completed(futures) devuelve un iterable que yield cada Future al terminar (orden de llegada)."""
    print("\n=== as_completed(): procesar según van terminando ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        # Tareas con duraciones distintas para ver orden de llegada
        futures = {
            executor.submit(tarea, i, 2.1 * (i + 1)): i
            for i in range(5)
        }

        # hacer pausa de 1 minuto

        for future in concurrent.futures.as_completed(futures):
            ident = futures[future]
            try:
                r = future.result()
                print(f"  tarea {ident} terminó: {r}")
            except Exception as e:
                print(f"  tarea {ident} falló: {e}")

def ejemplo_wait():
    """wait(futures, return_when=...) bloquea hasta FIRST_COMPLETED o ALL_COMPLETED."""
    print("\n=== wait(): FIRST_COMPLETED vs ALL_COMPLETED ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(tarea, i, 0.2 * (i + 1)) for i in range(5)]
        done, pending = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
        print(f"  FIRST_COMPLETED: {len(done)} done, {len(pending)} pending")
        for f in done:
            print(f"    resultado: {f.result()}")
        # Esperar al resto
        done2, pending2 = concurrent.futures.wait(pending)
        print(f"  Tras esperar resto: todos done")

def ejemplo_future_cancel():
    """cancel() intenta cancelar; solo funciona si la tarea no empezó (p.ej. en cola)."""
    print("\n=== Future.cancel() ===")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f1 = executor.submit(time.sleep, 2)  # esta ocupa el único worker
        f2 = executor.submit(tarea, 99)      # esta espera en cola
        time.sleep(0.05)
        ok = f2.cancel()
        print(f"  cancel(f2) = {ok}  (puede ser True si aún no empezaba)")
        try:
            f2.result()
        except concurrent.futures.CancelledError:
            print("  f2 fue cancelada: CancelledError")
        f1.result()

def ejemplo_add_done_callback():
    """add_done_callback(fn) llama a fn(future) cuando la tarea termina."""
    print("\n=== add_done_callback() ===")
    def al_terminar(fut: concurrent.futures.Future):
        try:
            r = fut.result()
            print(f"  [callback] resultado = {r}")
        except Exception as e:
            print(f"  [callback] excepción: {e}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        f = executor.submit(tarea, 42, 0.2)
        f.add_done_callback(al_terminar)
        # result() para que el with espere
        f.result()


# ---------------------------------------------------------------------------
# ASYNCIO.FUTURE: promesa en el event loop; Task es una subclase que ejecuta una coroutine.
# ---------------------------------------------------------------------------

async def ejemplo_asyncio_future_manual():
    """asyncio.Future: creado con loop.create_future(); se completa con set_result/set_exception."""
    print("\n=== asyncio.Future (manual) ===")
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    async def completar_desde_otra_coroutine():
        await asyncio.sleep(0.2)
        fut.set_result(100)

    asyncio.create_task(completar_desde_otra_coroutine())
    r = await fut
    print(f"  await future = {r}")

async def ejemplo_task_es_future():
    """create_task(coro) devuelve una Task, que es un asyncio.Future; await Task = resultado de la coroutine."""
    print("\n=== Task como Future ===")
    async def coro(x: int):
        await asyncio.sleep(0.1)
        return x * 2

    t = asyncio.create_task(coro(21))
    print(f"  type(t) = {type(t).__name__}  (Task es subclase de Future)")
    print(f"  t.done() = {t.done()}")
    r = await t
    print(f"  await task = {r}, t.done() = {t.done()}")

async def ejemplo_gather_devuelve_resultados():
    """gather() espera varias coroutines y devuelve lista de resultados (orden preservado)."""
    print("\n=== asyncio.gather(): múltiples 'Futures' (coroutines) ===")
    async def trabajo(n: int):
        await asyncio.sleep(0.05 * n)
        return n

    resultados = await asyncio.gather(trabajo(1), trabajo(2), trabajo(3))
    print(f"  resultados: {resultados}")

async def ejemplo_as_completed_asyncio():
    """asyncio.as_completed() devuelve un iterable de coroutines que yield al terminar cada una."""
    print("\n=== asyncio.as_completed() ===")
    async def tarea(id_: int, delay: float):
        await asyncio.sleep(delay)
        return id_

    tasks = [asyncio.create_task(tarea(i, 0.1 * (4 - i))) for i in range(4)]
    for coro in asyncio.as_completed(tasks):
        r = await coro
        print(f"  terminó: {r}")

async def ejemplo_future_timeout_asyncio():
    """asyncio.wait_for(coro, timeout=...) cancela la tarea si supera el tiempo."""
    print("\n=== asyncio.wait_for (timeout) ===")
    async def lenta():
        await asyncio.sleep(10.0)
        return "ok"

    try:
        r = await asyncio.wait_for(lenta(), timeout=0.2)
    except asyncio.TimeoutError:
        print("  TimeoutError: tarea cancelada por timeout")


# ---------------------------------------------------------------------------
# Comparación: concurrent.futures.Future vs asyncio.Future
# ---------------------------------------------------------------------------
# concurrent.futures.Future: resultado de submit() en Thread/ProcessPool.
#   - result() bloquea el hilo. done(), cancelled(), exception(), add_done_callback().
# asyncio.Future: promesa en el event loop.
#   - await future no bloquea el hilo; cede al loop. set_result/set_exception desde el loop.
# Task es asyncio.Future + ejecución de una coroutine (create_task).
# No mezclar: son APIs distintas; run_in_executor devuelve asyncio.Future que envuelve el resultado del executor.
# ---------------------------------------------------------------------------


async def main_async():
    await ejemplo_asyncio_future_manual()
    await ejemplo_task_es_future()
    await ejemplo_gather_devuelve_resultados()
    await ejemplo_as_completed_asyncio()
    await ejemplo_future_timeout_asyncio()

import sys

if __name__ == "__main__":
    #ejemplo_future_done_result()
    #ejemplo_future_timeout()
    #ejemplo_future_exception()
    #ejemplo_as_completed()
 
    ejemplo_wait()
    sys.exit()

 
    ejemplo_future_cancel()
    ejemplo_add_done_callback()
    asyncio.run(main_async())
    print("\n--- Fin 14_future_profundizacion ---")
