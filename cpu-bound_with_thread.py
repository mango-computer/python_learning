import time
from concurrent.futures import ThreadPoolExecutor

def io():
    time.sleep(1)  # simula espera de red/disk

t0 = time.perf_counter()
io(); io()
t1 = time.perf_counter()
print("Secuencial:", t1 - t0)

t0 = time.perf_counter()
with ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(lambda _: io(), range(2)))
t1 = time.perf_counter()
print("Threads:", t1 - t0)


#Secuencial: 0.001612781998119317
#Threads: 0.0009232839984179009