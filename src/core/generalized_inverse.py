from sympy import Matrix

from . import generalized_inverse_i, generalized_inverse_ii, generalized_inverse_iii, generalized_inverse_iv

def ginv_type_I_II(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    # region Summary
    """
    :param sizes: Input matrix sizes (denoted as mxn)
    :param hyper_parameters: Hyper-parameters for numerical-analytical method (variable, discretes count (denoted as K),
                                                                               approximation center (denoted as t_nyu), scaling coefficient (denoted as H))
    :param matrix: Input matrix (denoted as A(t))
    """
    # endregion Summary

    # region Body

    # Get the number of rows and columns of the input matrix
    rows, columns = sizes

    # Separate the real and imaginary parts of the input matrix
    real_matrix, imaginary_matrix = matrix.as_real_imag()

    # If the input matrix is underdetermined or determined
    if rows <= columns:
        if hyper_parameters["use_analytical_method"]:
            # get the generalized inverse matrix using analytical method
            generalized_inverse, intermediate_results = generalized_inverse_i.analytical_method(real_matrix, imaginary_matrix)
        else:
            # get the generalized inverse matrix using the numerical-analytical method
            generalized_inverse, intermediate_results = generalized_inverse_i.numerical_analytical_method(sizes, real_matrix, imaginary_matrix, hyper_parameters)

    # Input matrix is overdetermined
    else:
        if hyper_parameters["use_analytical_method"]:
            # get the generalized inverse matrix using analytical method
            generalized_inverse, intermediate_results = generalized_inverse_ii.analytical_method(real_matrix, imaginary_matrix)
        else:
            # get the generalized inverse matrix using the numerical-analytical method
            generalized_inverse, intermediate_results = generalized_inverse_ii.numerical_analytical_method(sizes, real_matrix, imaginary_matrix, hyper_parameters)

    return generalized_inverse, intermediate_results

    # endregion Body

def ginv_type_III(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    # region Summary
    """
    :param sizes: Input matrix sizes (denoted as mxn)
    :param hyper_parameters: Hyper-parameters for numerical-analytical method (variable, discretes count (denoted as K),
                                                                               approximation center (denoted as t_nyu), scaling coefficient (denoted as H))
    :param matrix: Input matrix (denoted as A(t))
    """
    # endregion Summary

    # region Body

    # Separate the real and imaginary parts of the input matrix
    real_matrix, imaginary_matrix = matrix.as_real_imag()

    # Get the generalized inverse matrix using the numerical-analytical method
    generalized_inverse, intermediate_results = generalized_inverse_iii.numerical_analytical_method(sizes, real_matrix, imaginary_matrix, hyper_parameters)

    return generalized_inverse, intermediate_results

    # endregion Body

def ginv_type_IV(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    # region Summary
    """
    :param sizes: Input matrix sizes (denoted as mxn)
    :param hyper_parameters: Hyper-parameters for numerical-analytical method (variable, discretes count (denoted as K),
                                                                               approximation center (denoted as t_nyu), scaling coefficient (denoted as H))
    :param matrix: Input matrix (denoted as A(t))
    """
    # endregion Summary

    # region Body

    # Separate the real and imaginary parts of the input matrix
    real_matrix, imaginary_matrix = matrix.as_real_imag()

    # Get the generalized inverse matrix using the numerical-analytical method
    generalized_inverse, intermediate_results = generalized_inverse_iv.numerical_analytical_method(sizes, real_matrix, imaginary_matrix, hyper_parameters)

    return generalized_inverse, intermediate_results

    # endregion Body
