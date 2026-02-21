import time
from concurrent.futures import ThreadPoolExecutor
import asyncio
import sys


async def io():
    await asyncio.sleep(1)  # simula espera de red/disk
    print("******* Funcion io ejecutada **********")




async def main():
    coroutine_io = io()
    await coroutine_io

asyncio.run(main())

