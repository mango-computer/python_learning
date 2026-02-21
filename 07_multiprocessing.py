#!/usr/bin/env python3
"""
07 - MULTIPROCESSING
===================
Procesos tienen memoria separada; no comparten el GIL → paralelismo real.
Comunicación: Queue, Pipe, Value, Array (objetos compartidos).
Solo biblioteca estándar: multiprocessing. Python 3.10+
"""

import multiprocessing
import os
import time


def tarea_mostrar_pid(identificador: int):
    """Cada proceso tiene su propio PID."""
    print(f"  [proceso {identificador}] PID={os.getpid()}")
    time.sleep(7)


def ejemplo_process_basico():
    """Crear y arrancar un proceso. join() para esperar."""
    print("=== Process básico ===")
    print(f"[main] PID={os.getpid()}")
    p = multiprocessing.Process(target=tarea_mostrar_pid, args=(1,))
    p.start()
    p.join()
    print("[main] Proceso terminado.")


def ejemplo_varios_procesos():
    """Varios procesos en paralelo (paralelismo real en múltiples núcleos)."""
    print("\n=== Varios procesos ===")
    procesos = []
    for i in range(3):
        p = multiprocessing.Process(target=tarea_mostrar_pid, args=(i,))
        procesos.append(p)
        p.start()
        print(f"  [main] proceso {p.pid} iniciado")
        time.sleep(3)
    for p in procesos:
        p.join()
        print(f"  [main] proceso {p.pid} terminó")
    print("[main] Todos terminaron.")


# ---------------------------------------------------------------------------
# Queue entre procesos: multiprocessing.Queue (no queue.Queue).
# ---------------------------------------------------------------------------

def trabajador_que_escribe(q: multiprocessing.Queue, n: int):
    """Proceso que pone mensajes en la cola."""
    for i in range(n):
        q.put(f"mensaje-{i}")
        print(f"  [escritor] escribi {i}")
        time.sleep(3)
    q.put(None)  # señal de fin


def trabajador_que_lee(q: multiprocessing.Queue):
    """Proceso que saca mensajes de la cola."""
    while True:
        print(f"  [lector] esperando...")
        item = q.get()
        print(f"  [lector] recibí {item}")
        if item is None:
            break
        print(f"  [lector] recibí {item}")


def ejemplo_multiprocessing_queue():
    """Comunicación entre procesos con multiprocessing.Queue."""
    print("\n=== multiprocessing.Queue ===")
    cola = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=trabajador_que_escribe, args=(cola, 3))
    p2 = multiprocessing.Process(target=trabajador_que_lee, args=(cola,))
    p1.start()
    p2.start()
    p1.join()
    p2.join()


# ---------------------------------------------------------------------------
# Pipe: canal bidireccional entre dos procesos.
# ---------------------------------------------------------------------------

def proceso_hijo(conn: multiprocessing.Pipe):
    """Recibe por el pipe y responde."""
    msg = conn.recv()
    print(f"  [hijo] recibí: {msg}")
    conn.send("respuesta del hijo")
    conn.close()


def ejemplo_pipe():
    """Pipe: parent_conn, child_conn = multiprocessing.Pipe()."""
    print("\n=== Pipe ===")
    parent_conn, child_conn = multiprocessing.Pipe()
    p = multiprocessing.Process(target=proceso_hijo, args=(child_conn,))
    p.start()
    print(f"  [padre] enviando mensaje...")
    time.sleep(3)
    parent_conn.send("hola hijo")
    respuesta = parent_conn.recv()
    print(f"  [padre] respuesta: {respuesta}")
    parent_conn.close()
    p.join()


# ---------------------------------------------------------------------------
# Value y Array: memoria compartida entre procesos (tipos de ctypes).
# ---------------------------------------------------------------------------

def incrementar_valor_compartido(val: multiprocessing.Value, n: int):
    """Incrementa un Value compartido (con lock)."""
    for _ in range(n):
        with val.get_lock():
            val.value += 1


def ejemplo_value():
    """multiprocessing.Value(typecode, value) para un valor compartido."""
    print("\n=== Value (memoria compartida) ===")
    # 'i' = int, valor inicial 0
    valor = multiprocessing.Value("i", 0)
    N = 50_000
    p1 = multiprocessing.Process(target=incrementar_valor_compartido, args=(valor, N))
    p2 = multiprocessing.Process(target=incrementar_valor_compartido, args=(valor, N))
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print(f"  Valor esperado {2*N}, obtenido: {valor.value}")


def ejemplo_array():
    """multiprocessing.Array para un array compartido."""
    print("\n=== Array (memoria compartida) ===")
    arr = multiprocessing.Array("i", [0, 0, 0])  # 3 enteros

    def escribir_arr(idx: int, valor: int):
        arr[idx] = valor

    p1 = multiprocessing.Process(target=escribir_arr, args=(0, 10))
    p2 = multiprocessing.Process(target=escribir_arr, args=(1, 20))
    p3 = multiprocessing.Process(target=escribir_arr, args=(2, 30))
    for p in (p1, p2, p3):
        p.start()
    for p in (p1, p2, p3):
        p.join()
    print(f"  Array: {list(arr)}")


if __name__ == "__main__":
    # En Windows/multiprocessing es necesario proteger el punto de entrada.
    #ejemplo_process_basico()
    #ejemplo_varios_procesos()
    #ejemplo_multiprocessing_queue()
    #ejemplo_pipe()
    #ejemplo_value()
    ejemplo_array()
    print("\n--- Fin 07_multiprocessing ---")
