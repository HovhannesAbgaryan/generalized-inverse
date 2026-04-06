import sympy as sp


def find_derivatives(matrix, symbol, discretes_count):
    # region Summary
    """
    :param matrix: Input matrix whose elements are one-parameter functions (denoted as A(t))
    :param symbol: Symbol of the function parameter (denoted as t)
    :param discretes_count: Number of discretes for derivation (denoted as K)
    """
    # endregion Summary

    # region Body

    # Create a derivatives list and append the original matrix as 0th order derivative
    derivatives = list([matrix])

    # Calculate the 1st, 2nd, ..., Kth order derivatives
    for _ in range(1, discretes_count):
        # differentiate the matrix with respect to symbol
        derivative = sp.diff(matrix, symbol)

        # append the Kth order derivative to the list
        derivatives.append(derivative)

        # replace the matrix with its derivative for the next iteration
        matrix = derivative

    return derivatives

    # endregion Body


def compute_discretes(derivatives, symbol, scaling_coefficient, approximation_center):
    # region Summary
    """
    :param derivatives: List of matrix derivatives
    :param symbol: Symbol of the function parameter (denoted as t)
    :param scaling_coefficient: Scaling coefficient that equalizes the dimensions of the originals and their images (denoted as H)
    :param approximation_center: Center of approximation for Taylor decompositions (denoted as t_nyu)
    """
    # endregion Summary

    # region Body

    # Create an empty list for discretes
    discretes = list()

    # For all derivatives
    for k in range(len(derivatives)):
        # calculate the matrix discretes according to the Pukhov differential transform
        discrete = (scaling_coefficient ** k / sp.factorial(k)) * derivatives[k].subs(symbol, approximation_center)

        # append the discrete to the list
        discretes.append(discrete)

    return discretes

    # endregion Body
