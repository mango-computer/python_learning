#!/usr/bin/env python3
"""
13 - SEMAPHORE: PROFUNDIZACIÓN
===============================
Cuándo usar Semaphore vs Lock vs ThreadPoolExecutor.
Casos reales: rate limiting, límite de conexiones.
acquire/release explícitos, timeout, BoundedSemaphore.
threading y asyncio. Solo biblioteca estándar. Python 3.10+
"""

import asyncio
import threading
import time
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor


# ---------------------------------------------------------------------------
# ¿SEMAPHORE vs LOCK vs THREADPOOLEXECUTOR?
# ---------------------------------------------------------------------------
#
# LOCK (mutex): solo 1 thread en la sección a la vez.
#   Uso: proteger variable compartida, evitar race condition.
#
# SEMAPHORE(n): hasta n threads en la sección a la vez.
#   Uso: limitar acceso a recurso compartido (conexiones BD, API, archivos).
#   Los threads pueden venir de varios pools o ser manuales.
#
# THREADPOOLEXECUTOR(max_workers=n): máximo n tareas en paralelo en ese pool.
#   Uso: "ejecuto muchas funciones, máximo n a la vez". Las tareas pasan por el pool.
#   Si solo quieres limitar concurrencia de tareas, el pool basta.
#
# Cuándo Semaphore: cuando el límite es de un RECURSO que usan hilos de distintos
# orígenes, o en asyncio (no hay pool de coroutines).
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# THREADING: acquire/release explícitos (alternativa a "with")
# ---------------------------------------------------------------------------

def ejemplo_acquire_release_explicito():
    """acquire() bloquea; release() libera. Siempre liberar en finally si usas explícito."""
    print("=== Semaphore: acquire/release explícitos ===")
    sem = threading.Semaphore(2)

    def tarea(id_: int):
        sem.acquire()
        try:
            print(f"  [t{id_}] dentro (adquirí)")
            time.sleep(0.2)
        finally:
            sem.release()
            print(f"  [t{id_}] fuera (liberé)")

    threads = [threading.Thread(target=tarea, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ---------------------------------------------------------------------------
# acquire(timeout=...): no bloquear indefinidamente si el recurso está saturado.
# ---------------------------------------------------------------------------


@contextmanager
def sem_with_cleanup(sem: threading.Semaphore):
    sem.acquire()
    try:
        yield
    finally:
        sem.release()
        print("Free Resources")


def ejemplo_acquire_timeout():
    """acquire(timeout=X) devuelve True si obtuvo el permiso, False si expiró el tiempo."""
    print("\n=== Semaphore: acquire(timeout=...) ===")
    sem = threading.Semaphore(1)  # solo 1 hueco

    def tarea_larga(id_: int):
        with sem_with_cleanup(sem):
            print(f"  [t{id_}] dentro (2s)")
            time.sleep(2.0)

    def tarea_con_timeout(id_: int):
        if sem.acquire(timeout=0.3):
            try:
                print(f"  [t{id_}] obtuve el semáforo")
                time.sleep(0.1)
            finally:
                sem.release()
        else:
            print(f"  [t{id_}] timeout: no pude entrar en 0.3s, sigo sin bloquear")

    t1 = threading.Thread(target=tarea_larga, args=(0,))
    t2 = threading.Thread(target=tarea_con_timeout, args=(1,))
    t1.start()
    time.sleep(0.05)  # t1 ya está dentro
    t2.start()
    t1.join()
    t2.join()


# ---------------------------------------------------------------------------
# BoundedSemaphore: el valor nunca supera el inicial (detecta release() de más).
# ---------------------------------------------------------------------------

def ejemplo_bounded_semaphore():
    """BoundedSemaphore(n): como Semaphore(n), pero release() falla si superas n."""
    print("\n=== BoundedSemaphore ===")
    # Semaphore normal: si haces release() de más, el contador sube (bug difícil de rastrear).
    # BoundedSemaphore: release() lanza ValueError si ya estás en n.
    sem = threading.BoundedSemaphore(1)

    def adquisicion_correcta():
        sem.acquire()
        try:
            time.sleep(0.1)
        finally:
            sem.release()

    threading.Thread(target=adquisicion_correcta).start()
    time.sleep(0.2)
    # sem.release() sin acquire previo en este thread -> ValueError con BoundedSemaphore
    try:
        sem.release()
        print("  (no debería llegar aquí con BoundedSemaphore)")
    except ValueError:
        print("  BoundedSemaphore: release() sin acquire previo -> ValueError (correcto)")


# ---------------------------------------------------------------------------
# Caso real: rate limiting a un recurso compartido (p.ej. API externa).
# ---------------------------------------------------------------------------

recurso_simulado = []
sem_recurso = threading.Semaphore(3)  # máximo 3 accesos concurrentes

def acceder_recurso(id_thread: int, operacion: str):
    """Simula llamada a API/BD: máximo 3 a la vez."""
    if not sem_recurso.acquire(timeout=1.0):
        print(f"  [t{id_thread}] rate limit: no pude acceder en 2s")
        return
    try:
        print(f"  [t{id_thread}] accediendo al recurso...")
        time.sleep(1.0)
        recurso_simulado.append((id_thread, operacion))
    finally:
        sem_recurso.release()

def ejemplo_rate_limiting():
    """Múltiples threads compiten por un recurso con límite de 3 concurrentes."""
    print("\n=== Caso real: rate limiting (máx 3 concurrentes) ===")
    recurso_simulado.clear()

    threads = [threading.Thread(target=acceder_recurso, args=(i, "read")) for i in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  Accesos completados: {len(recurso_simulado)}")


# ---------------------------------------------------------------------------
# Semaphore vs ThreadPoolExecutor: mismo efecto en este caso, diferentes herramientas.
# ---------------------------------------------------------------------------

def ejemplo_semaphore_vs_pool():
    """Si solo quieres 'máx N tareas a la vez', ThreadPoolExecutor(max_workers=N) basta.
    Semaphore es útil cuando el límite es de un recurso que usan hilos de varios orígenes."""
    print("\n=== Semaphore vs Pool: mismo límite, diferente uso ===")
    print("  Pool: tareas pasan por ese executor; límite de workers.")
    print("  Semaphore: límite de quién puede entrar a una sección; los hilos vienen de donde sea.")
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(time.sleep, 0.1) for _ in range(4)]
        for f in futures:
            f.result()
    print("  Pool: 4 tareas, 2 workers -> 2 a la vez. No necesitas Semaphore.")


# ---------------------------------------------------------------------------
# ASYNCIO: asyncio.Semaphore, mismo concepto.
# ---------------------------------------------------------------------------

async def acceder_recurso_async(sem: asyncio.Semaphore, id_: int):
    async with sem:
        print(f"  [coro {id_}] dentro del recurso")
        await asyncio.sleep(0.2)
    print(f"  [coro {id_}] fuera")

async def ejemplo_asyncio_semaphore():
    """En asyncio no hay pool de coroutines; Semaphore limita cuántas coroutines
    pueden estar en una sección a la vez."""
    print("\n=== asyncio.Semaphore: límite en coroutines ===")
    sem = asyncio.Semaphore(2)
    await asyncio.gather(*(acceder_recurso_async(sem, i) for i in range(5)))


# ---------------------------------------------------------------------------
# Caso real async: límite de conexiones concurrentes (p.ej. descargas).
# ---------------------------------------------------------------------------

async def descarga_simulada(sem: asyncio.Semaphore, url_id: int):
    async with sem:
        print(f"  [download] iniciando url-{url_id}")
        await asyncio.sleep(0.3)
        print(f"  [download] url-{url_id} lista")
    return f"datos-{url_id}"

async def ejemplo_descargas_limitadas():
    """Limitar descargas concurrentes para no saturar red o servidor."""
    print("\n=== Caso real async: descargas limitadas (máx 2) ===")
    sem = asyncio.Semaphore(2)
    resultados = await asyncio.gather(*(descarga_simulada(sem, i) for i in range(6)))
    print(f"  Resultados: {resultados}")


if __name__ == "__main__":
    ejemplo_acquire_release_explicito()
    ejemplo_acquire_timeout()
    ejemplo_bounded_semaphore()
    ejemplo_rate_limiting()
    ejemplo_semaphore_vs_pool()
    asyncio.run(ejemplo_asyncio_semaphore())
    asyncio.run(ejemplo_descargas_limitadas())
    print("\n--- Fin 13_semaphore_profundizacion ---")
