import time
from concurrent.futures import ThreadPoolExecutor

def cpu(n: int) -> int:
    s = 0
    for i in range(n):
        s += i*i
    return s

N = 30_000_00  # ajusta si tarda poco/mucho

t0 = time.perf_counter()
cpu(N)
cpu(N)
t1 = time.perf_counter()
print("Secuencial:", t1 - t0)

t0 = time.perf_counter()
with ThreadPoolExecutor(max_workers=2) as ex:
    list(ex.map(cpu, [N, N]))
t1 = time.perf_counter()
print("Threads:", t1 - t0)
