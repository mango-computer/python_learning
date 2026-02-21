#!/usr/bin/env python3
"""
06 - COMUNICACIÓN ENTRE THREADS
================================
queue.Queue: cola thread-safe. Un thread pone (put), otro saca (get).
Patrón producer-consumer sin necesidad de Lock manual.
Solo biblioteca estándar: queue. Python 3.10+
"""

import queue
import threading
import time


def ejemplo_queue_basica():
    """Queue: put() añade, get() saca. Blocking por defecto."""
    print("=== Queue básica ===")
    cola = queue.Queue()

    def productor():
        time.sleep(20)
        for i in range(10):
            cola.put(f"item-{i}")
            print(f"  [productor] puse item-{i}")
        cola.put(None)  # señal de "no hay más" (convención)

    def consumidor():
        while True:
            item = cola.get()  # bloquea si la cola está vacía
            if item is None:
                break
            print(f"  [consumidor] obtuve {item}")
        print("  [consumidor] fin")

    t1 = threading.Thread(target=productor)
    t2 = threading.Thread(target=consumidor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def ejemplo_queue_con_timeout():
    """get(timeout=...) y put(timeout=...) para no bloquear indefinidamente."""
    print("\n=== Queue con timeout ===")
    cola = queue.Queue(maxsize=2)  # máximo 2 elementos

    def productor():
        for i in range(8):
            try:
                print(f"  [p] intentando put x{i}")
                time.sleep(3)
                cola.put(f"x{i}", timeout=1)
                print(f"  [p] put x{i}")
            except queue.Full:
                print("  [p] cola llena, espero...")
        print("  [p] fin")
        cola.put(None)

    def consumidor():
        while True:
            try:
                print("  [c] esperando...")
                #time.sleep(3)
                item = cola.get(timeout=1)
                if item is None:
                    break
                print(f"  [c] get {item}")
            except queue.Empty:
                print("  [c] cola vacía (timeout)")

    t1 = threading.Thread(target=productor)
    t2 = threading.Thread(target=consumidor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def ejemplo_queue_task_done_join():
    """task_done() + join(): el productor espera a que se procesen todos los ítems."""
    print("\n=== Queue task_done / join ===")
    cola = queue.Queue()
    N = 3

    def productor():
        for i in range(N):
            cola.put(i)
            print(f"  [productor] puse {i}")
        cola.join()  # bloquea hasta que se llame task_done() N veces
        print("  [productor] Todos los ítems procesados.")

    def consumidor():
        for _ in range(N):
            item = cola.get()
            print(f"  [consumidor] proceso {item}")
            time.sleep(0.1)
            cola.task_done()  # indica que este ítem está procesado
            print(f"  [consumidor] task_done {item}")
        print("  [consumidor] fin")

    t1 = threading.Thread(target=productor)
    t2 = threading.Thread(target=consumidor)
    t1.start()
    t2.start()
    t1.join()
    t2.join()


def ejemplo_lifo_priority():
    """Queue por defecto es FIFO. queue.LifoQueue y queue.PriorityQueue también son thread-safe."""
    print("\n=== LifoQueue (último en entrar, primero en salir) ===")
    lifo = queue.LifoQueue()
    lifo.put(1)
    lifo.put(2)
    lifo.put(3)
    print("  get:", lifo.get(), lifo.get(), lifo.get())  # 3 2 1

    print("=== PriorityQueue (menor prioridad primero) ===")
    pq = queue.PriorityQueue()
    pq.put((2, "segundo"))
    pq.put((1, "primero"))
    pq.put((3, "tercero"))
    print("  get:", pq.get()[1], pq.get()[1], pq.get()[1])  # primero segundo tercero


if __name__ == "__main__":
    ejemplo_queue_basica()
    #ejemplo_queue_con_timeout()
    #ejemplo_queue_task_done_join()
    #ejemplo_lifo_priority()
    print("\n--- Fin 06_comunicacion_threads ---")
