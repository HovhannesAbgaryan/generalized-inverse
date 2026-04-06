import sympy as sp

from ..utils.discretes_calculation import find_derivatives, compute_discretes

# region Summary
"""
THEORY (MATHEMATICS) PAPER
Title: Definition of Complex One-Parameter Generalized Moore-Penrose Inverses Using Differential Transformations
Author(s): S.H. Simonyan, H.S. Abgaryan, A.G. Avetisyan
Journal: Computational and Mathematical Methods (SCOPUS, Q3; Web of Science)
DOI: https://doi.org/10.1155/cmm4/8895138
Parameters: 2025, Issue 1
Publication date: 08/2025

IMPLEMENTATION (CODE) PAPER
Title: Software Implementation of Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices Using Differential Transformations (I)
Author(s): H.S. Abgaryan
Journal: Proceedings of NAS RA and NPUA: Technical Sciences Series
DOI: https://doi.org/10.53297/0002306X-2024.v77.4-520
Parameters: 2024, № 4, pages 520-527
Publication date: 12/2025
"""
# endregion Summary

# region Functions

def numerical_analytical_method(sizes, real_matrix, imaginary_matrix, hyper_parameters):
    # region Summary
    """
    :param sizes: Input matrix sizes (denoted as mxn)
    :param real_matrix: Real part of input matrix (denoted as A_1(t))
    :param imaginary_matrix: Imaginary part of input matrix (denoted as A_2(t))
    :param hyper_parameters: Hyper-parameters for numerical-analytical method (variable, discretes count (denoted as K),
                                                                               approximation center (denoted as t_nyu), scaling coefficient (denoted as H))
    """
    # endregion Summary

    # region Body

    # Take the shape of input matrix
    m, n = sizes

    # region Derivatives and discretes

    # Calculate K = 0, 1, ..., K derivatives of real matrix
    real_matrix_derives = find_derivatives(real_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])

    # Calculate K = 0, 1, ..., K derivatives of imaginary matrix
    imaginary_matrix_derives = find_derivatives(imaginary_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])

    # Calculate K = 0, 1, ..., K discretes of real matrix (denoted as A_1(K))
    real_matrix_discretes = compute_discretes(real_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])

    # Calculate K = 0, 1, ..., K discretes of imaginary matrix (denoted as A_2(K))
    imaginary_matrix_discretes = compute_discretes(imaginary_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])

    # endregion Derivatives and discretes

    # region X_1(K), X_2(K)

    # Build the full 2n×2m block-matrix A(0)
    A_0 = sp.Matrix([
                    [real_matrix_discretes[0].T, imaginary_matrix_discretes[0].T],
                    [imaginary_matrix_discretes[0].T, -real_matrix_discretes[0].T]
                  ])

    # Compute pseudo-inverse of the A(0) block-matrix according to Equation (20)
    X_0 = A_0.pinv()

    # Create a list for X_1(K) block-matrices and append the X_1(0) block-matrix (according to the Equation (20))
    X1_K = [X_0[0:m, 0:n].T]

    # Create a list for X_2(K) block-matrices and append the X_2(0) block-matrix (according to the Equation (20))
    X2_K = [-X_0[0:m, n:2*n].T]

    # For K in [1; K-1]
    for K in range(1, hyper_parameters["discretes_count"]):
        # create mx2m block-matrix for sum in Equation (23) filled with 0s
        summa = [sp.zeros(m, m), sp.zeros(m, m)]

        # for i in [0; K-1]
        for i in range(K):
            # calculate corresponding element of summa block-matrix as matrix multiplication of X_1(i) and X_2(i) with A_1(K-i) and A_2(K-i)
            summa[0] += (X1_K[i].T * real_matrix_discretes[K - i].T - X2_K[i].T * imaginary_matrix_discretes[K - i].T)
            summa[1] += (X1_K[i].T * imaginary_matrix_discretes[K - i].T + X2_K[i].T * real_matrix_discretes[K - i].T)

        # calculate X_1(K) block-matrix as matrix multiplication of summa and X(0) block-matrices, and append it to the list of X_1(K) block-matrices
        x1 = -summa[0] * X1_K[0].T + summa[1] * X2_K[0].T
        X1_K.append(x1.T)

        # calculate X_2(K) block-matrix as matrix multiplication of summa and X(0) block-matrices, and append it to the list of X_2(K) block-matrices
        x2 = summa[0] * X2_K[0].T + summa[1] * X1_K[0].T
        X2_K.append(-x2.T)

    # endregion X_1(K), X_2(K)

    # region X_1(t), X_2(t)

    # Create a SymPy matrix X_1(t) nxm filled with 0s
    X1_t = sp.zeros(n, m)

    # Create a SymPy matrix X_2(t) nxm filled with 0s
    X2_t = sp.zeros(n, m)

    # Restore the X_1(t) and X_2(t) matrices according to the Equation (17)
    for K in range(hyper_parameters["discretes_count"]):
        X1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X1_K[K]
        X2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X2_K[K]

    # endregion X1(t), X2(t)

    # region A+(t)

    # Calculate the generalized inverse A+(t) matrix according to the Equation (5)
    generalized_inverse = X1_t + sp.I * X2_t

    # endregion A+(t)

    # Create the dictionary of intermediate results to use in generating calculation steps
    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                X1_K = X1_K, X2_K = X2_K, X1_t = X1_t, X2_t = X2_t)

    return generalized_inverse, intermediate_results

    # endregion Body

# endregion Functions
