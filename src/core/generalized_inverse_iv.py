import sympy as sp

from ..utils.discretes_calculation import find_derivatives, compute_discretes

# region Summary
"""
THEORY (MATHEMATICS) PAPER
Title: To The Definition of Complex One-Parameter Generalized Inverse Moore-Penrose Matrices (II)
Author(s): S.H. Simonyan, A.G. Avetisyan, H.S. Abgaryan
Journal: Proceedings of NPUA: Information Technologies, Electronics, Radio Engineering
DOI: https://doi.org/10.53297/18293336-2025.1-9
Parameters: 2025, № 1, pages 9-19
Publication date: 10/2025

IMPLEMENTATION (CODE) PAPER
Title: Software Implementation of Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices Using Differential Transformations (II)
Author(s): H.S. Abgaryan
Journal: Proceedings of NAS RA and NPUA: Technical Sciences Series
DOI: https://doi.org/10.53297/0002306X-2025.v78.1-130
Parameters: 2025, № 1, pages 130-136
Publication date: 02/2026
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
    A_0 = sp.Matrix(
        [
            [real_matrix_discretes[0].T, -imaginary_matrix_discretes[0].T],
            [imaginary_matrix_discretes[0].T, real_matrix_discretes[0].T],
        ]
    )

    # Compute pseudo-inverse of the A(0) block-matrix according to Equation (21)
    X_0 = A_0.pinv()

    # Create a list for X_1(K) block-matrices and append the X_1(0) block-matrix (according to the Equation (26))
    X1_K = [X_0[0:m, 0:n].T]

    # Create a list for X_2(K) block-matrices and append the X_2(0) block-matrix (according to the Equation (26))
    X2_K = [X_0[m:2*m, 0:n].T]

    # # For K in [1; K-1]
    for K in range(1, hyper_parameters["discretes_count"]):
        # create nx2n block-matrix for sum in Equation (29) filled with 0s
        summa = [sp.zeros(n, n), sp.zeros(n, n)]

        # for i in [1; K]
        for i in range(1, K + 1):
            # calculate corresponding element of summa block-matrix as matrix multiplication of A_1(i) and A_2(i) with X_1(K-i) and X_2(K-i)
            summa[0] += (real_matrix_discretes[i].T * X1_K[K - i].T - imaginary_matrix_discretes[i].T * X2_K[K - i].T)
            summa[1] += (imaginary_matrix_discretes[i].T * X1_K[K - i].T + real_matrix_discretes[i].T * X2_K[K - i].T)

        # calculate X_1(K) block-matrix as matrix multiplication of X(0) and summa block-matrices, and append it to the list of X_1(K) block-matrices
        x1 = -X1_K[0].T * summa[0] + X2_K[0].T * summa[1]
        X1_K.append(x1.T)

        # calculate X_2(K) block-matrix as matrix multiplication of X(0) and summa block-matrices, and append it to the list of X_2(K) block-matrices
        x2 = -X2_K[0].T * summa[0] - X1_K[0].T * summa[1]
        X2_K.append(x2.T)

    # endregion X_1(K), X_2(K)

    # region X1(t), X2(t)

    # Create a SymPy matrix X_1(t) nxm filled with 0s
    X1_t = sp.zeros(n, m)

    # Create a SymPy matrix X_2(t) nxm filled with 0s
    X2_t = sp.zeros(n, m)

    # Restore the X_1(t) and X_2(t) matrices according to the Equation (18)
    for K in range(hyper_parameters["discretes_count"]):
        X1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X1_K[K]
        X2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X2_K[K]

    # endregion X1(t), X2(t)

    # region A+(t)

    # Calculate the generalized inverse A+(t) matrix according to the Equation (6)
    generalized_inverse = X1_t + sp.I * X2_t

    # endregion A+(t)

    # Create the dictionary of intermediate results to use in generating calculation steps
    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                X1_K = X1_K, X2_K = X2_K, X1_t = X1_t, X2_t = X2_t)

    return generalized_inverse, intermediate_results

    # endregion Body

# endregion Functions
