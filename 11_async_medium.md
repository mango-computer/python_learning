# 11 - Async/await medium — Mapas y diagramas

Todos los ejemplos corren en **un solo hilo**; el event loop programa las coroutines. Los diagramas muestran la interacción entre ellas.

---

## Contexto: un hilo, event loop

```mermaid
flowchart LR
    subgraph Thread["Hilo principal"]
        EL[Event loop]
        EL --> C1[Coro 1]
        EL --> C2[Coro 2]
        EL --> Cn[Coro N]
    end
```

---

## Ejemplo: Timeout (`ejemplo_timeout`) — wait_for

`wait_for(tarea_lenta(5.0), timeout=0.5)`: la tarea quiere 5s; el timeout cancela a 0.5s.

```mermaid
sequenceDiagram
    participant Main as main
    participant WF as wait_for
    participant Task as tarea_lenta(5)

    Main->>WF: await wait_for(tarea_lenta(5), timeout=0.5)
    WF->>Task: crea Task, programa en el loop
    loop Cada poco
        Task->>Task: await sleep (interno)
        WF->>WF: comprueba tiempo
    end
    Note over WF: 0.5s → TimeoutError
    WF->>Task: cancel()
    WF-->>Main: lanza TimeoutError
```

La coroutine `tarea_lenta` se **cancela** cuando expira el timeout; el event loop sigue en el mismo hilo.

---

## Ejemplo: asyncio.Lock (`ejemplo_async_lock`)

Dos coroutines incrementan un contador compartido; el lock asegura que solo una modifica a la vez.

```mermaid
flowchart TB
    subgraph Shared["Estado compartido (mismo hilo)"]
        contador[contador]
        lock[asyncio.Lock]
    end

    subgraph Coroutines["Coroutines (alternan en el loop)"]
        C1[incrementar_con_lock 10_000]
        C2[incrementar_con_lock 10_000]
    end

    C1 -->|async with lock| lock
    C2 -->|async with lock| lock
    lock --> contador
```

Solo una coroutine tiene el lock a la vez; la otra espera en `async with lock` (cede al loop sin bloquear el hilo).

---

## Ejemplo: asyncio.Queue (`ejemplo_async_queue`) — productor/consumidor

Un productor pone ítems; un consumidor los saca. Cola compartida, mismo hilo.

```mermaid
flowchart LR
    P[productor_async\nput item-0,1,2\nput None]
    Q[asyncio.Queue]
    C[consumidor_async\nget → procesa\nget None → fin]

    P -->|await put| Q
    Q -->|await get| C
```

```mermaid
sequenceDiagram
    participant P as productor
    participant Q as Queue
    participant C as consumidor

    P->>Q: put item-0
    C->>Q: get → item-0
    P->>Q: put item-1
    C->>Q: get → item-1
    P->>Q: put item-2
    C->>Q: get → item-2
    P->>Q: put None
    C->>Q: get → None
    C->>C: break, fin
```

El event loop alterna entre productor y consumidor cuando hacen `await cola.put/get`.

---

## Ejemplo: gather con return_exceptions (`ejemplo_gather_exceptions`)

Tres tareas: una OK, una que lanza `ValueError`, otra OK. Con `return_exceptions=True` no se cancela el resto.

```mermaid
flowchart TB
    G[gather return_exceptions=True]
    G --> T1[tarea_ok 1 → 1]
    G --> T2[tarea_falla → ValueError]
    G --> T3[tarea_ok 2 → 2]

    G --> Result["[1, ValueError(...), 2]"]
```

El resultado es una lista: posiciones 0 y 2 son valores; posición 1 es la excepción. Todo en el mismo hilo.

---

## Ejemplo: asyncio.Semaphore (`ejemplo_semaphore`)

Cuatro coroutines compiten por un semáforo(2): como máximo 2 dentro de la sección a la vez.

```mermaid
flowchart TB
    subgraph Sem["Semaphore(2)"]
        S[2 permisos]
    end

    subgraph Tasks["4 tareas"]
        T0[tarea_con_sem 0]
        T1[tarea_con_sem 1]
        T2[tarea_con_sem 2]
        T3[tarea_con_sem 3]
    end

    T0 -->|async with sem| S
    T1 -->|async with sem| S
    T2 -->|async with sem| S
    T3 -->|async with sem| S
```

**Orden típico:** 0 y 1 entran; a 0.3s salen; entran 2 y 3; salen. El event loop despierta a las que esperan en `sem.acquire()` cuando hay permiso.
