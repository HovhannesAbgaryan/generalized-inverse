import sympy
import math

def find_derivatives(matrix, symbol, discretes_count):
    derivatives = list([matrix])
    for _ in range(1, discretes_count):
        derivative = sympy.diff(matrix, symbol)
        derivatives.append(derivative)
        matrix = derivative
    return derivatives


def compute_discretes(derivatives, symbol, scaling_coefficient, value):
    discretes = list()
    for k in range(len(derivatives)):
        discrete = (scaling_coefficient ** k / math.factorial(k)) * derivatives[k].subs(symbol, value)
        discretes.append(discrete)
    return discretes