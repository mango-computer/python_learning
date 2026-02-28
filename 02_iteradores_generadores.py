#!/usr/bin/env python3
"""
02 - ITERADORES Y GENERADORES
=============================
Un iterable tiene __iter__(); un iterador tiene __next__().
Los generadores (yield) son la forma más simple de crear iteradores.
Objetos nativos: iter(), next(), yield. Python 3.10+
"""


def ejemplo_iter_next():
    """iter() obtiene un iterador; next() pide el siguiente valor."""
    print("=== iter() y next() ===")
    lista = [10, 20, 3]
    it = iter(lista)
    print(next(it))  # 10
    print(next(it))  # 20
    print(next(it))  # 30
    #print(next(it))  # StopIteration
    # next(it)  # StopIteration si descomentas


def ejemplo_iterador_manual():
    """Implementar un iterador: __iter__ devuelve self, __next__ devuelve el siguiente."""
    print("\n=== Iterador manual (clase) ===")

    class ContadorHasta:
        def __init__(self, tope):
            self.tope = tope
            self.actual = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.actual >= self.tope:
                raise StopIteration
            valor = self.actual
            self.actual += 1
            return valor

    for n in ContadorHasta(3):
        print(n, end=" ")
    print()


def ejemplo_generador_yield():
    """Un generador es una función con yield; cada yield "pausa" y devuelve un valor."""
    print("\n=== Generador con yield ===")

    def cuenta_hasta(n):
        for i in range(n):
            yield i  # pausa aquí y devuelve i

    gen = cuenta_hasta(3)
    print(next(gen))  # 0 1 2
    print(next(gen))  # 0 1 2
    print(next(gen))  # 0 1 2


    # next(gen) -> StopIteration

    for x in cuenta_hasta(3):
        print(x, end=" ")
    print()


def ejemplo_expresion_generadora():
    """(x for x in ...) es un generador, no una lista. Ahorra memoria."""
    print("\n=== Expresión generadora ===")
    g = (x * 2 for x in range(4))
    print(list(g))  # [0, 2, 4, 6]
    # g ya está agotado
    cuadrados = (x**2 for x in range(5))
    for v in cuadrados:
        print(v, end=" ")
    print()


def ejemplo_por_que_importa_para_concurrencia():
    """
    Los generadores producen valores de uno en uno (lazy).
    Más adelante verás que threads/processes también "producen" resultados
    de forma asíncrona; el concepto de "flujo de datos paso a paso" es similar.
    """
    print("\n=== Flujo paso a paso (concepto para más adelante) ===")

    def infinito_paso_a_paso():
        i = 0
        while True:
            yield i
            i += 1

    g = infinito_paso_a_paso()
    for _ in range(3):
        print(next(g), end=" ")
    print("  (generador sigue vivo, no hemos creado lista infinita)")


if __name__ == "__main__":
    ejemplo_iter_next()
    ejemplo_iterador_manual()
    ejemplo_generador_yield()
    ejemplo_expresion_generadora()
    ejemplo_por_que_importa_para_concurrencia()
    print("\n--- Fin 02_iteradores_generadores ---")
