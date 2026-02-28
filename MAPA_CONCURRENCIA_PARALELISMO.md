# Mapa: Concurrencia y paralelismo en Python

Referencia de modelos, librerías, comunicación segura, sincronización y casos de uso. Incluye biblioteca estándar y menciones a librerías externas habituales.

---

## 1. Modelos de concurrencia y paralelismo

| Modelo | Qué es | Unidades de ejecución | Comparten memoria | GIL | Cuándo usarlo |
|--------|--------|------------------------|-------------------|-----|----------------|
| **Threads** | Varios flujos en un mismo proceso | Hilos (threads) del SO | Sí (heap del proceso) | Sí, un hilo ejecuta Python a la vez | I/O-bound; tareas que esperan red/disco |
| **Procesos** | Varios procesos del SO | Procesos independientes | No (cada uno su espacio) | No (cada proceso su GIL) | CPU-bound; paralelismo real |
| **Async (asyncio)** | Un hilo, muchas tareas cooperativas | Coroutines (no son threads) | Sí (mismo proceso) | No compite (un solo hilo) | I/O-bound; muchas conexiones/esperas |

- **Concurrencia:** varias tareas “en curso”; pueden alternar en el tiempo (threads, async) o ejecutarse en paralelo (procesos).
- **Paralelismo:** ejecución real simultánea (varios núcleos). En Python, solo con **procesos** (o código fuera del GIL).
- **Coroutine (asyncio):** función `async` que cede con `await`; no es un thread ni un proceso; vive en el event loop de un solo hilo.

---

## 2. Coroutines en los distintos modelos

| Contexto | ¿Hay “coroutines”? | Rol |
|----------|---------------------|-----|
| **Threads** | No; hay funciones que ejecutan los threads | Cada thread ejecuta una función (o un método) de forma síncrona. |
| **Procesos** | No; hay funciones que ejecutan los procesos | Cada proceso ejecuta un `target` (función) en su espacio. |
| **Asyncio** | Sí | Las coroutines (`async def`) son el modelo; el loop las programa y las ejecuta cuando hacen `await`. |
| **Concurrent.futures** | No; hay “futures” (promesas de resultado) | `submit(fn)` programa una función; el resultado es un `Future`. No es coroutine. |
| **Mezcla async + threads/procesos** | Sí en el hilo principal | Las coroutines pueden delegar trabajo bloqueante con `run_in_executor()` (thread o process pool); el resultado vuelve al mundo async vía `await`. |

**Resumen:** “Coroutine” en Python se refiere a **asyncio** (`async`/`await`). En threading y multiprocessing no hay coroutines; hay funciones ejecutadas por threads o procesos. Los Futures (concurrent.futures o asyncio.Future) son promesas de resultado, no coroutines.

---

## 3. Mapa de librerías por modelo

### 3.1 Procesos (multiprocessing)

| Librería / Módulo | Uso principal |
|-------------------|----------------|
| **multiprocessing** (stdlib) | `Process`, `Queue`, `Pipe`, `Value`, `Array`, `Lock`, `Manager` |
| **concurrent.futures.ProcessPoolExecutor** (stdlib) | Pool de procesos; `submit()`, `map()`; API alto nivel |
| **multiprocessing.Manager** (stdlib) | Objetos compartidos entre procesos (listas, dicts, etc.) vía proxy |

**Comunicación entre procesos (stdlib):**
- `multiprocessing.Queue`: cola entre procesos (serialización automática).
- `multiprocessing.Pipe`: canal punto a punto (dos conexiones).
- `multiprocessing.Value` / `Array`: memoria compartida (tipos C).

**Sincronización entre procesos (stdlib):**
- `multiprocessing.Lock`, `multiprocessing.Event`, `multiprocessing.Condition`, `multiprocessing.Semaphore` (equivalentes a threading, para procesos).

---

### 3.2 Threads (threading)

| Librería / Módulo | Uso principal |
|-------------------|----------------|
| **threading** (stdlib) | `Thread`, `Lock`, `RLock`, `Event`, `Condition`, `Semaphore`, `BoundedSemaphore` |
| **queue** (stdlib) | `Queue`, `LifoQueue`, `PriorityQueue` (thread-safe) |
| **concurrent.futures.ThreadPoolExecutor** (stdlib) | Pool de threads; `submit()`, `map()` |

**Comunicación entre threads (stdlib):**
- `queue.Queue`: cola thread-safe; `put()`/`get()` bloquean el hilo.
- Variables compartidas en memoria (con sincronización vía Lock, etc.).

**Sincronización entre threads (stdlib):**
- `threading.Lock` / `RLock`: exclusión mutua.
- `threading.Event`: señal uno-a-muchos (wait/set).
- `threading.Condition`: wait/notify con condición.
- `threading.Semaphore` / `BoundedSemaphore`: límite de N en una sección.

---

### 3.3 Async (asyncio)

| Librería / Módulo | Uso principal |
|-------------------|----------------|
| **asyncio** (stdlib) | Event loop, `async`/`await`, `create_task`, `gather`, `wait`, `wait_for` |
| **asyncio.Queue** (stdlib) | Cola entre coroutines; `await put()`/`await get()` |
| **asyncio.Lock**, **Semaphore**, **Event** (stdlib) | Sincronización entre coroutines (no bloquean el hilo) |
| **run_in_executor** (asyncio) | Ejecutar código bloqueante en ThreadPool o ProcessPool sin bloquear el loop |

**Comunicación entre coroutines (stdlib):**
- `asyncio.Queue`: producer-consumer async.
- Variables compartidas (mismo hilo; cuidado con race si hay varios `await` que alternan).

**Sincronización async (stdlib):**
- `asyncio.Lock`: exclusión mutua entre coroutines.
- `asyncio.Semaphore`: límite de N coroutines en una sección.
- `asyncio.Event`: señal entre coroutines.
- `asyncio.Condition`: wait/notify en async.

**Librerías externas (mención):**
- **aiohttp**, **httpx** (async): HTTP async.
- **uvloop**: event loop más rápido (reemplazo de asyncio loop).

---

## 4. Estructuras de datos y comunicación segura

| Necesidad | Threads | Procesos | Async |
|-----------|---------|----------|--------|
| Cola FIFO | `queue.Queue` | `multiprocessing.Queue` | `asyncio.Queue` |
| Cola LIFO / prioridad | `queue.LifoQueue`, `queue.PriorityQueue` | — (o Manager) | — (emular con asyncio.Queue) |
| Canal punto a punto | — (Queue o variable + Lock) | `multiprocessing.Pipe` | — (Queue o Event) |
| Valor compartido simple | Variable + Lock | `multiprocessing.Value` | Variable (un hilo; Lock si varias coroutines) |
| Array compartido | Variable + Lock o Array compartido (no en stdlib) | `multiprocessing.Array` | Variable / estructura en memoria |
| Estructuras complejas compartidas | Objeto + Lock (o queue para mensajes) | `multiprocessing.Manager().list()`, etc. | Objeto en memoria (coordinado con Lock si hace falta) |

Regla práctica: usar **colas o canales** para comunicar; usar **locks/semáforos** para proteger accesos a estado compartido.

---

## 5. Sincronización: resumen por modelo

| Primitiva | Threads (stdlib) | Procesos (stdlib) | Async (stdlib) |
|-----------|------------------|-------------------|----------------|
| Exclusión mutua (1 a la vez) | `threading.Lock`, `RLock` | `multiprocessing.Lock` | `asyncio.Lock` |
| Señal (esperar / despertar) | `threading.Event` | `multiprocessing.Event` | `asyncio.Event` |
| Wait/Notify con condición | `threading.Condition` | `multiprocessing.Condition` | `asyncio.Condition` |
| Límite N en sección | `threading.Semaphore` | `multiprocessing.Semaphore` | `asyncio.Semaphore` |
| Timeout en espera | `Lock.acquire(timeout=...)`, etc. | Igual | `asyncio.wait_for(coro, timeout=...)` |

No mezclar primitivas de un modelo con otro (p. ej. no usar `threading.Lock` dentro de una coroutine para coordinar con otras coroutines; usar `asyncio.Lock`).

---

## 6. Casos de uso habituales

| Caso de uso | Modelo recomendado | Comunicación / sincronización típica |
|-------------|--------------------|--------------------------------------|
| Muchas peticiones HTTP/API (I/O) | Async (asyncio) | `aiohttp`/`httpx`; opcional `asyncio.Semaphore` para límite de concurrencia |
| Descargas/upload en paralelo (I/O) | Threads (ThreadPoolExecutor) o async | `queue.Queue` o `asyncio.Queue`; límite con Semaphore o max_workers |
| Cálculo pesado (CPU) | Procesos (ProcessPoolExecutor o multiprocessing) | `multiprocessing.Queue` o `Pipe`; resultados por `Future.result()` si usas futures |
| Servidor de sockets / WebSockets | Async (asyncio) | `asyncio.Queue`, `asyncio.Lock` según diseño |
| Worker pool (tareas a cola) | Threads o procesos según I/O vs CPU | `queue.Queue` (threads) o `multiprocessing.Queue` (procesos) |
| Un productor, N consumidores | Cualquiera según I/O/CPU | Cola del modelo correspondiente; sentinela o Event para cierre |
| Rate limiting / límite de recursos | Cualquiera | Semaphore (del mismo modelo) |
| Leer muchos ficheros | Async o threads | Async: `asyncio.to_thread` o `run_in_executor`; threads: ThreadPoolExecutor |
| Pipeline (etapas en cadena) | Threads o procesos | Varias colas entre etapas |

---

## 7. Cuándo usar cada modelo (resumen)

- **Asyncio:** Muchas tareas I/O-bound en un solo proceso; quieres un solo hilo y control fino con `await` (timeouts, cancelación, miles de conexiones).
- **Threads:** I/O-bound con APIs síncronas que no quieres reescribir; librerías que bloquean; ThreadPoolExecutor para “N tareas a la vez”.
- **Procesos:** CPU-bound; aprovechar varios núcleos; aislamiento entre tareas (un fallo no tumba todo el proceso).

**Mezcla común:** asyncio en el hilo principal + `run_in_executor(ThreadPoolExecutor)` o `ProcessPoolExecutor` para trabajo bloqueante o CPU-bound, manteniendo el flujo async con `await`.

---

## 8. Relación con los módulos del curso

| Tema del mapa | Módulos del curso |
|---------------|-------------------|
| Threads, sincronización, colas | 04, 05, 06 |
| Procesos, Queue, Pipe, Value, Array | 07 |
| Pools (Futures) | 08, 14 |
| Async básico/medium/avanzado | 10, 11, 12 |
| Semaphore en detalle | 13 |
| Future (promesas) | 14 |
| Conceptos (GIL, I/O vs CPU) | 03 |

Este documento sirve como mapa de referencia; los ejemplos ejecutables están en los archivos `.py` del curso.
