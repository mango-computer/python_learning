# Curso: Loop, Concurrencia y Paralelismo en Python

Curso progresivo desde cero hasta nivel experto. **Solo biblioteca estándar** (Python 3.10+). Sin librerías externas ni APIs en desuso.

## Índice del curso

| # | Módulo | Contenido |
|---|--------|-----------|
| 01 | [Fundamentos del loop](01_fundamentos_loop.py) | `for`, `while`, `range`, `enumerate`, `zip`, iterables |
| 02 | [Iteradores y generadores](02_iteradores_generadores.py) | `__iter__`, `__next__`, `yield`, expresiones generadora |
| 03 | [Conceptos: concurrencia y paralelismo](03_conceptos_concurrencia.py) | GIL, CPU vs I/O, cuándo usar qué |
| 04 | [Threading básico](04_threading_basico.py) | `threading.Thread`, `start()`, `join()`, daemon |
| 05 | [Sincronización](05_sincronizacion.py) | `Lock`, `RLock`, `Event`, `Condition`, `Semaphore` |
| 06 | [Comunicación entre threads](06_comunicacion_threads.py) | `queue.Queue`, producer-consumer |
| 07 | [Multiprocessing](07_multiprocessing.py) | `Process`, `Queue`, `Pipe`, `Value`, `Array` |
| 08 | [concurrent.futures](08_concurrent_futures.py) | `ThreadPoolExecutor`, `ProcessPoolExecutor`, `submit`, `map` |
| 09 | [Práctica integrada](09_practica_integrada.py) | Ejemplo que combina threads, colas y sincronización |
| 10 | [Async/await básico](10_async_basico.py) | `async def`, `await`, `asyncio.run()`, `create_task`, `gather` |
| 11 | [Async/await medium](11_async_medium.py) | `wait_for` (timeout), `Lock`, `Queue`, `Semaphore`, errores en `gather` |
| 12 | [Async/await avanzado](12_async_advanced.py) | `run_in_executor`, producer-consumer async, cancelación, `asyncio.wait` |
| 13 | [Semaphore: profundización](13_semaphore_profundizacion.py) | Cuándo Semaphore vs Lock vs Pool, casos reales, acquire/release, BoundedSemaphore |
| 14 | [Future: profundización](14_future_profundizacion.py) | concurrent.futures.Future, asyncio.Future, Task, done/result/timeout, as_completed, wait |

## Cómo usar

Cada archivo es ejecutable y contiene teoría en comentarios + ejemplos que puedes correr:

```bash
cd curso_loop_concurrencia
python 01_fundamentos_loop.py
python 02_iteradores_generadores.py
# ...
```

Descomenta o modifica los bloques que quieras probar. Requiere **Python 3.10+** (recomendado 3.12).

## Objetos nativos usados

- **Loop:** `for`, `while`, `break`, `continue`, `else` en loops
- **Iteración:** `iter()`, `next()`, `range()`, `enumerate()`, `zip()`
- **Threads:** `threading.Thread`, `threading.Lock`, `threading.Event`, `threading.Condition`, `threading.Semaphore`
- **Colas:** `queue.Queue` (thread-safe)
- **Procesos:** `multiprocessing.Process`, `multiprocessing.Queue`, `multiprocessing.Pipe`, `multiprocessing.Value`, `multiprocessing.Array`
- **Alto nivel:** `concurrent.futures.ThreadPoolExecutor`, `concurrent.futures.ProcessPoolExecutor`, `Future`
- **Async:** `asyncio.run()`, `async def`, `await`, `asyncio.create_task()`, `asyncio.gather()`, `asyncio.Queue`, `asyncio.Lock`, `asyncio.Semaphore`, `asyncio.wait_for()`, `run_in_executor()`
