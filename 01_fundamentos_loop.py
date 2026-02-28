#!/usr/bin/env python3
"""
01 - FUNDAMENTOS DEL LOOP
=========================
Todo en Python que puedes recorrer en un "for" es un iterable.
El loop es la base para entender después iteradores, threads y concurrencia.
Solo biblioteca estándar. Python 3.10+
"""


def ejemplo_for_basico():
    """Loop for sobre una secuencia (lista)."""
    print("=== for sobre lista ===")
    frutas = ["manzana", "pera", "uva"]
    for f in frutas:
        print(f)  # f toma cada valor en orden


def ejemplo_range():
    """range() genera números sin crear lista en memoria (es perezoso en Py3)."""
    print("\n=== range(stop) ===")
    for i in range(5):
        print(i, end=" ")  # 0 1 2 3 4
    print()

    print("=== range(start, stop) ===")
    for i in range(2, 6):
        print(i, end=" ")  # 2 3 4 5
    print()

    print("=== range(start, stop, step) ===")
    for i in range(0, 10, 2):
        print(i, end=" ")  # 0 2 4 6 8
    print()


def ejemplo_enumerate():
    """Tener índice y valor en el mismo loop."""
    print("\n=== enumerate ===")
    frutas = ["manzana", "pera", "uva"]
    for indice, nombre in enumerate(frutas):
        print(f"{indice}: {nombre}")
    # Con inicio distinto de 0:
    for indice, nombre in enumerate(frutas, start=1):
        print(f"  #{indice} -> {nombre}")


def ejemplo_zip():
    """Recorrer dos (o más) secuencias en paralelo."""
    print("\n=== zip ===")
    nombres = ["Ana", "Luis", "María"]
    edades = [20, 25, 30]
    for nombre, edad in zip(nombres, edades):
        print(f"{nombre}: {edad} años")
    # zip se detiene en la secuencia más corta
    for a, b in zip([1, 2, 3], ["x", "y"]):
        print(a, b)  # (1,'x'), (2,'y')


def ejemplo_while():
    """Loop mientras se cumpla condición."""
    print("\n=== while ===")
    n = 0
    while n < 3:
        print(n)
        n += 1


def ejemplo_break_continue_else():
    """break sale del loop; continue pasa a la siguiente iteración; else se ejecuta si no hubo break."""
    print("\n=== break / continue / else ===")
    for i in range(5):
        if i == 2:
            continue  # salta el 2
        if i == 4:
            break  # sale antes de imprimir 4
        print(i, end=" ")
    else:
        print("(no se ejecuta porque hubo break)")
    print()

    # else en for: se ejecuta cuando el loop termina "normalmente"
    for i in range(3):
        print(i, end=" ")
    else:
        print(" <- loop terminó sin break")


def ejemplo_iterable_nativo():
    """Objetos nativos iterables: str, dict, set, archivos."""
    print("\n=== str es iterable (caracteres) ===")
    for letra in "hola":
        print(letra, end=" ")
    print()

    print("=== dict: iterar keys, values, items ===")
    d = {"a": 1, "b": 2}
    for k in d:
        print(k, end=" ")
    print()
    for k, v in d.items():
        print(f"{k}={v}", end=" ")
    print()


if __name__ == "__main__":
    ejemplo_for_basico()
    ejemplo_range()
    ejemplo_enumerate()
    ejemplo_zip()
    ejemplo_while()
    ejemplo_break_continue_else()
    ejemplo_iterable_nativo()
    
    print("\n--- Fin 01_fundamentos_loop ---")
