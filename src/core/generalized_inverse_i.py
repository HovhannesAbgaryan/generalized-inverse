import sympy as sp

from ..utils.discretes_calculation import find_derivatives, compute_discretes
from ..utils.cleaning import clean_matrix

# region Summary
"""
THEORY (MATHEMATICS) PAPER
Title: Decomposition Methods for Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices (I)
Author(s): S.H. Simonyan, M.G. Chilingaryan, H.S. Abgaryan
Journal: Proceedings of NPUA: Information Technologies, Electronics, Radio Engineering
DOI: https://doi.org/10.53297/18293336-2023.2-9
Parameters: 2023, № 2, pages 9-21
Publication date: 03/2024

IMPLEMENTATION (CODE) PAPER
Title: Software Implementation of Decomposition Methods for Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices (I)
Author(s): S.H. Simonyan, A.V. Melikyan, H.S. Abgaryan
Journal: Proceedings of NPUA: Information Technologies, Electronics, Radio Engineering
DOI: https://doi.org/10.53297/18293336-2024.1-9
Parameters: 2024, № 1, pages 9-19
Publication date: 09/2024
"""
# endregion Summary

# region Functions

def analytical_method(real_matrix, imaginary_matrix):
    # region Summary
    """
    :param real_matrix: Real part of input matrix (denoted as A_1(t))
    :param imaginary_matrix: Imaginary part of input matrix (denoted as A_2(t))
    """
    # endregion Summary

    # region Body

    # region B_1(t), B_2(t), B(t)

    # Calculate B_1(t) matrix according to the Equation (8)
    B1_t = real_matrix * real_matrix.T + imaginary_matrix * imaginary_matrix.T

    # Calculate B_2(t) matrix according to the Equation (9)
    B2_t = imaginary_matrix * real_matrix.T - real_matrix * imaginary_matrix.T

    # Denote B(t) = B_1(t) + j * B_2(t)
    B_t = B1_t + B2_t * sp.I

    # endregion B_1(t), B_2(t), B(t)

    # region X(t), X_1(t), X_2(t)

    # Calculate X(t) = B+(t) according to the Equation (10)
    X_t = sp.expand(B_t.pinv())

    # Separate real (denoted as X_1(t)) and imaginary (denoted as X_2(t)) parts of X(t)
    X1_t, X2_t = X_t.as_real_imag()

    # endregion X(t), X_1(t), X_2(t)

    # region A+(t)

    # Calculate real part of Equation (16)
    real = real_matrix.T * X1_t + imaginary_matrix.T * X2_t

    # Calculate imaginary part of Equation (16)
    imaginary = sp.expand(real_matrix.T * X2_t - imaginary_matrix.T * X1_t)

    # Calculate generalized inverse matrix (denoted as A+(t)) according to the Equation (16)
    generalized_inverse = real + imaginary * sp.I

    # endregion A+(t)

    # Create a dictionary for calculation's intermediate results
    intermediate_results = dict(B1_t = B1_t, B2_t = B2_t, X1_t = X1_t, X2_t = X2_t)

    return generalized_inverse, intermediate_results

    # endregion Body

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

    # Take the number of rows of input matrix
    m = sizes[0]

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

    # region B_1(K), B_2(K), B(K)

    # Create an empty list for B_1(K) matrix discretes
    B1_matrix_discretes = list()

    # Create an empty list for B_2(K) matrix discretes
    B2_matrix_discretes = list()

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]):
        # create B_1(K) mxm matrix filled with 0s
        B1_K = sp.zeros(m, m)

        # create B_2(K) mxm matrix filled with 0s
        B2_K = sp.zeros(m, m)

        # for i in [0; K]
        for i in range(K + 1):
            # calculate B_1(K) matrix discrete according to the Equation (8) (or equations on page 17)
            B1_K += (real_matrix_discretes[i] * real_matrix_discretes[K - i].T + imaginary_matrix_discretes[i] * imaginary_matrix_discretes[K - i].T)

            # calculate B_2(K) matrix discrete according to the Equation (9) (or equations on page 17)
            B2_K += (imaginary_matrix_discretes[i] * real_matrix_discretes[K - i].T - real_matrix_discretes[i] * imaginary_matrix_discretes[K - i].T)

        # append B_1(K) matrix discrete to the list of B_1(K) matrix discretes
        B1_matrix_discretes.append(B1_K)

        # append B_2(K) matrix discrete to the list of B_2(K) matrix discretes
        B2_matrix_discretes.append(B2_K)

    # Create an empty list for B(K) block-matrices
    B_K = []

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]):
        # append corresponding B(K) block-matrix (according to the notation (22)) to the list of B(K) block-matrices
        B_K.append([
            [B1_matrix_discretes[K], -B2_matrix_discretes[K]],
            [B2_matrix_discretes[K], B1_matrix_discretes[K]]
        ])

    # Build the full 2m×2m block matrix B(0)
    B_0 = sp.Matrix.vstack(
        sp.Matrix.hstack(B1_matrix_discretes[0], -B2_matrix_discretes[0]),
              sp.Matrix.hstack(B2_matrix_discretes[0],  B1_matrix_discretes[0])
    )

    # endregion B_1(K), B_2(K), B(K)

    # region X(K), X_1(K), X_2(K)

    # Compute pseudo-inverse of the B(0) block matrix according to Equation (27)
    X_0 = B_0.pinv()

    # Create a list for X(K) block-matrices and append the X(0) block-matrix (according to the Equation (27))
    X_K = [
        [
            [X_0[0:m, 0:m],   X_0[0:m, m:2*m]],
            [X_0[m:2*m, 0:m], X_0[m:2*m, m:2*m]]
        ]
    ]

    # For K in [1; K-1]
    for K in range(1, hyper_parameters["discretes_count"]):
        # create 2mx2m block-matrix for sum in Equation (31) filled with 0s
        summa = [
            [sp.zeros(m, m), sp.zeros(m, m)],
            [sp.zeros(m, m), sp.zeros(m, m)]
        ]

        # for i in [1; K]
        for i in range(1, K + 1):
            # calculate corresponding element of summa block-matrix as matrix multiplication of B(i) and X(K-i) block-matrices
            summa[0][0] += B_K[i][0][0] * X_K[K - i][0][0] + B_K[i][0][1] * X_K[K - i][1][0]
            summa[0][1] += B_K[i][0][0] * X_K[K - i][0][1] + B_K[i][0][1] * X_K[K - i][1][1]
            summa[1][0] += B_K[i][1][0] * X_K[K - i][0][0] + B_K[i][1][1] * X_K[K - i][1][0]
            summa[1][1] += B_K[i][1][0] * X_K[K - i][0][1] + B_K[i][1][1] * X_K[K - i][1][1]

        # calculate X(K) block-matrix as matrix multiplication of -X(0) and summa block-matrices, and append it to the list of X(K) block-matrices
        X_K.append(
            [
                [-X_K[0][0][0] * summa[0][0] + -X_K[0][0][1] * summa[1][0], -X_K[0][0][0] * summa[0][1] + -X_K[0][0][1] * summa[1][1]],
                [-X_K[0][1][0] * summa[0][0] + -X_K[0][1][1] * summa[1][0], -X_K[0][1][0] * summa[0][1] + -X_K[0][1][1] * summa[1][1]]
            ])

    # Create an empty list for X_1(K) matrix discretes
    X1_K = list()

    # Create an empty list for X_2(K) matrix discretes
    X2_K = list()

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]): # + 1
        # take the element at (0, 0) of X(K) block-matrix as X_1(K) matrix discrete (according to the notation (22))
        X1_K.append(X_K[K][0][0])

        # take the element at (1, 0) of X(K) block-matrix as X_2(K) matrix discrete (according to the notation (22))
        X2_K.append(X_K[K][1][0])

    # endregion X(K), X_1(K), X_2(K)

    # region X_1(t), X_2(t)

    # Create a SymPy matrix X_1(t) mxm filled with 0s
    X1_t = sp.zeros(m, m)

    # Create a SymPy matrix X_2(t) mxm filled with 0s
    X2_t = sp.zeros(m, m)

    # Restore the X_1(t) and X_2(t) matrices according to the Equation (26)
    for K in range(hyper_parameters["discretes_count"]):
        X1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X1_K[K]
        X2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * X2_K[K]

    # Clean numerical noise from X1(t) and X2(t)
    X1_t = clean_matrix(X1_t, tolerance=1e-10)
    X2_t = clean_matrix(X2_t, tolerance=1e-10)

    # endregion X_1(t), X_2(t)

    # region A+(t)

    # Calculate the generalized inverse A+(t) matrix according to the Equation (16)
    a = real_matrix - sp.I * imaginary_matrix
    x = X1_t + sp.I * X2_t
    generalized_inverse = sp.expand(a.T * x)

    # Clean numerical noise from the final result
    generalized_inverse = clean_matrix(generalized_inverse, tolerance=1e-10)

    # endregion A+(t)

    # Create the dictionary of intermediate results to use in generating calculation steps
    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                B1_K = B1_matrix_discretes, B2_K = B2_matrix_discretes, X1_K = X1_K, X2_K = X2_K, X1_t = X1_t, X2_t = X2_t)

    return generalized_inverse, intermediate_results

    # endregion Body

# endregion Functions
