## Mapa: Async de alto nivel vs bajo nivel (Python 3.10+)

Referencia rápida para entender qué partes de `asyncio` y del ecosistema async son **alto nivel** (lo que usas en aplicaciones) y cuáles son **bajo nivel** (tripas del event loop, sólo si necesitas control fino). Solo incluye APIs **actuales** de la biblioteca estándar; nada obsoleto.

---

### 1. Idea general

- **Alto nivel**: API pensada para uso diario en aplicaciones.
  - Abstrae detalles del event loop.
  - Maneja creación/cierre del loop, tareas y errores comunes.
  - Legible, fácil de enseñar y de mantener.
- **Bajo nivel**: API pensada para librerías, frameworks o integraciones especiales.
  - Te da acceso directo al **event loop**, a **Futures** y a llamadas de programación de callbacks.
  - Permite modelos avanzados (varios loops, integración con hilos/procesos, sockets de bajo nivel).
  - Es más fácil romper cosas o mezclar mal modelos.

Regla práctica: **en aplicaciones, usa alto nivel siempre que puedas; baja a bajo nivel sólo si sabes exactamente por qué lo necesitas.**

---

### 2. Alto nivel en `asyncio`

Pensado para que puedas escribir aplicaciones async sin tocar casi nunca el loop directamente.

- **Arranque y ciclo de vida del loop**
  - `asyncio.run(coro())`
    - Crea un event loop, ejecuta la coroutine principal y lo cierra correctamente.
    - Maneja detalles de política del loop y limpieza de tareas pendientes.

- **Creación y gestión de tareas**
  - `asyncio.create_task(coro())`
    - Envuelve la coroutine en una `Task` y la agenda en el event loop actual.
    - No crea un thread; la tarea corre en el **mismo hilo** del loop.
  - `await asyncio.gather(c1, c2, ..., return_exceptions=False)`
    - Ejecuta concurrentemente varias coroutines y espera a que todas terminen.
  - `await asyncio.wait(…)`
    - Espera a un conjunto de tareas/Futures con opciones (FIRST_COMPLETED, FIRST_EXCEPTION, etc.).

- **Control de tiempo y cancelación**
  - `await asyncio.sleep(segundos)`
    - Cede al event loop durante un tiempo sin bloquear el hilo.
  - `await asyncio.wait_for(coro, timeout=segundos)`
    - Ejecuta una coroutine con timeout; lanza `asyncio.TimeoutError` si se pasa.
  - `task.cancel()`
    - Marca una `Task` para cancelación; la coroutine verá un `CancelledError` en el siguiente `await`.

- **Sincronización y comunicación async**
  - `asyncio.Queue`
    - Cola producer-consumer entre coroutines (`await put`, `await get`).
  - `asyncio.Lock`, `asyncio.Semaphore`, `asyncio.Event`, `asyncio.Condition`
    - Primitivas clásicas pero en versión async (no bloquean el hilo, solo la coroutine).

- **E/S de alto nivel**
  - `asyncio.open_connection`, `asyncio.start_server`
    - Streams TCP client/server en modo async.

Estas funciones son las que aparecen en los módulos 10, 11 y 12 del curso; son la “cara amable” del mundo async.

---

### 3. Bajo nivel en `asyncio`

Te dejan manipular directamente el event loop y los objetos internos. Útil si:

- Estás escribiendo una **librería async**.
- Necesitas **integrarte con código no estándar** (por ejemplo, sockets custom, bucles de eventos externos o GUI).
- Quieres manejar **varios loops en varios hilos**.

#### 3.1 Gestión explícita del event loop

- `asyncio.get_running_loop()`
  - Devuelve el loop que está ejecutando la coroutine actual.
  - Permite acceder a métodos como `run_in_executor`, `create_task`, etc.
- `asyncio.new_event_loop()`, `asyncio.set_event_loop(loop)`
  - Crear un loop manualmente (por ejemplo, en un hilo secundario).
- Métodos del loop:
  - `loop.run_until_complete(coro)`
  - `loop.run_forever()`, `loop.stop()`, `loop.close()`
  - `loop.call_soon(callback, *args)`
  - `loop.call_later(delay, callback, *args)`
  - `loop.call_at(when, callback, *args)`

En aplicaciones normales, `asyncio.run()` ya usa internamente estas piezas y no necesitas llamarlas tú.

#### 3.2 Futures, Tasks y callbacks

- `asyncio.Future`
  - Promesa de un resultado que se completará en el futuro.
  - Normalmente no creas Futures manualmente en aplicaciones; los crean librerías o el loop.
- `loop.create_task(coro)` / `asyncio.create_task(coro)` (alto nivel sobre el mismo concepto)
  - Registra una coroutine como `Task` en el loop actual.
- `future.add_done_callback(callback)`
  - Ejecuta `callback` cuando el Future se completa (patrón más bajo nivel que `await`).

#### 3.3 Sockets y E/S de bajo nivel

APIs pensadas para trabajar con sockets crudos sin pasar por los streams de alto nivel:

- `loop.sock_recv(sock, nbytes)`
- `loop.sock_sendall(sock, data)`
- `loop.add_reader(fd, callback, *args)` / `loop.add_writer(fd, callback, *args)`

En muchas aplicaciones de usuario final, usas directamente streams (`open_connection`, `start_server`) o una librería de más alto nivel (por ejemplo, HTTP async), sin tocar estos métodos.

---

### 4. Mezcla async + threads/procesos (run_in_executor y afines)

Este es un punto intermedio: desde async (alto nivel) puedes usar funciones que delegan trabajo a **pools de hilos o procesos** sin bloquear el event loop.

- `loop.run_in_executor(executor, func, *args)`
  - Ejecuta `func(*args)` en:
    - un `ThreadPoolExecutor` (trabajo I/O bloqueante o librerías síncronas),
    - o un `ProcessPoolExecutor` (trabajo CPU pesado).
  - Devuelve un `Future` que puedes `await`.
- `asyncio.to_thread(func, *args)` (Python 3.9+)
  - Atajo de alto nivel para mandar una función bloqueante a un hilo del pool por defecto:
    - `await asyncio.to_thread(bloqueante, 1, 2, 3)`

Aquí se mezclan:

- **Alto nivel**: tú haces simplemente `await` a algo (`to_thread`, `run_in_executor`).
- **Bajo nivel**: por debajo, el loop coordina la integración con `ThreadPoolExecutor` / `ProcessPoolExecutor`.

---

### 5. Librerías async habituales (no deprecadas)

Además de la biblioteca estándar, en proyectos async reales se usan a menudo librerías externas **actuales** (ecosistema Python 3.10+):

- **HTTP / Web**
  - `aiohttp`: cliente y servidor HTTP async.
  - `httpx` (en modo async): cliente HTTP moderno.
- **Event loop alternativo**
  - `uvloop`: implementación muy rápida del event loop compatible con `asyncio`.

En este curso, los ejemplos de código se centran en la **biblioteca estándar** (`asyncio`, `concurrent.futures`) para evitar dependencias externas, pero es importante conocer estas librerías porque son las que verás en proyectos reales.

---

### 6. Regla de oro para elegir nivel

- **Aplicación o script async “normal”:**
  - Usa `asyncio.run`, `async def`/`await`, `create_task`, `gather`, `Queue`, `Lock`, `Semaphore`, `wait_for`, `to_thread`.
- **Caso avanzado / librería / integración rara:**
  - Usa explícitamente el loop (`get_running_loop`, `new_event_loop`, `run_in_executor`, sockets de bajo nivel, Futures manuales).

Si tienes dudas, empieza **siempre** con las APIs de alto nivel; solo deberías bajar de nivel cuando el alto nivel ya no te deja expresar lo que necesitas.

