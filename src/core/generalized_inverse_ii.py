import sympy as sp

from ..utils.discretes_calculation import find_derivatives, compute_discretes
from ..utils.cleaning import clean_matrix

# region Summary
"""
THEORY (MATHEMATICS) PAPER
Title: Decomposition Methods for Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices (II)
Author(s): S.H. Simonyan, M.G. Chilingaryan, H.S. Abgaryan
Journal: Proceedings of NAS RA and NPUA: Technical Sciences Series
DOI: https://doi.org/10.53297/0002306X-2023.v76.4-514
Parameters: 2023, № 4, pages 514-524
Publication date: 05/2024

IMPLEMENTATION (CODE) PAPER
Title: Software Implementation of Decomposition Methods for Determining Complex One-Parameter Generalized Inverse Moore-Penrose Matrices (II)
Author(s): S.H. Simonyan, A.V. Melikyan, H.S. Abgaryan
Journal: Proceedings of NPUA: Information Technologies, Electronics, Radio Engineering
DOI: https://doi.org/10.53297/18293336-2024.2-24
Parameters: 2024, № 2, pages 24-34
Publication date: 04/2025
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

    # region C_1(t), C_2(t), C(t)

    # Calculate C_1(t) matrix according to the Equation (3)
    C1_t = real_matrix.T * real_matrix + imaginary_matrix.T * imaginary_matrix

    # Calculate C_2(t) matrix according to the Equation (4)
    C2_t = real_matrix.T * imaginary_matrix - imaginary_matrix.T * real_matrix

    # Denote C(t) = C_1(t) + j * C_2(t)
    C_t = C1_t + C2_t * sp.I

    # endregion C_1(t), C_2(t), C(t)

    # region Y(t), Y_1(t), Y_2(t)

    # Calculate Y(t) = C+(t) according to the Equation (5)
    Y_t = sp.expand(C_t.pinv())

    # Separate real (denoted as Y_1(t)) and imaginary (denoted as Y_2(t)) parts of Y(t)
    Y1_t, Y2_t = Y_t.as_real_imag()

    # endregion Y(t), Y_1(t), Y_2(t)

    # region A+(t)

    # Calculate real part of Equation (11)
    real = Y1_t * real_matrix.T + Y2_t * imaginary_matrix.T

    # Calculate imaginary part of Equation (11)
    imaginary = sp.expand(Y2_t * real_matrix.T - Y1_t * imaginary_matrix.T)

    # Calculate generalized inverse matrix (denoted as A+(t)) according to the Equation (11)
    generalized_inverse = real + imaginary * sp.I

    # endregion A+(t)

    # Create a dictionary for calculation's intermediate results
    intermediate_results = dict(C1_t = C1_t, C2_t = C2_t, Y1_t = Y1_t, Y2_t = Y2_t)

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

    # Take the number of columns of input matrix
    n = sizes[1]

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

    # region C_1(K), C_2(K), C(K)

    # Create an empty list for C_1(K) matrix discretes
    C1_matrix_discretes = list()

    # Create an empty list for C_2(K) matrix discretes
    C2_matrix_discretes = list()

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]):
        # create C_1(K) mxm matrix filled with 0s
        C1_K = sp.zeros(n, n)

        # create C_2(K) mxm matrix filled with 0s
        C2_K = sp.zeros(n, n)

        # for i in [0; K]
        for i in range(K + 1):
            # calculate C_1(K) matrix discrete according to the Equation (3)
            C1_K += (real_matrix_discretes[i].T * real_matrix_discretes[K - i] + imaginary_matrix_discretes[i].T * imaginary_matrix_discretes[K - i])

            # calculate C_2(K) matrix discrete according to the Equation (4)
            C2_K += (real_matrix_discretes[i].T * imaginary_matrix_discretes[K - i] - imaginary_matrix_discretes[i].T * real_matrix_discretes[K - i])

        # append C_1(K) matrix discrete to the list of C_1(K) matrix discretes
        C1_matrix_discretes.append(C1_K)

        # append C_2(K) matrix discrete to the list of C_2(K) matrix discretes
        C2_matrix_discretes.append(C2_K)

    # Create an empty list for B(K) block-matrices
    C_K = []

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]):
        # append corresponding B(K) block-matrix (according to the notation (22)) to the list of B(K) block-matrices
        C_K.append([
            [C1_matrix_discretes[K], -C2_matrix_discretes[K]],
            [C2_matrix_discretes[K], C1_matrix_discretes[K]]
        ])

    # Build the full 2n×2n block-matrix B(0)
    C_0 = sp.Matrix.vstack(
        sp.Matrix.hstack(C1_matrix_discretes[0], -C2_matrix_discretes[0]),
              sp.Matrix.hstack(C2_matrix_discretes[0],  C1_matrix_discretes[0])
    )

    # endregion C_1(K), C_2(K), C(K)

    # region Y(K), Y_1(K), Y_2(K)

    # Compute pseudo-inverse of the C(0) block-matrix according to Equation (22)
    Y_0 = C_0.pinv()

    # Create a list for Y(K) block-matrices and append the Y(0) block-matrix (according to the Equation (22))
    Y_K = [
        [
            [Y_0[0:n, 0:n], Y_0[0:n, n:2*n]],
            [Y_0[n:2*n, 0:n], Y_0[n:2*n, n:2*n]]
        ]
    ]

    # For K in [1; K-1]
    for K in range(1, hyper_parameters["discretes_count"]):
        # create 2nx2n block-matrix for sum in Equation (26) filled with 0s
        summa = [
            [sp.zeros(n, n), sp.zeros(n, n)],
            [sp.zeros(n, n), sp.zeros(n, n)]
        ]

        # for i in [1; K]
        for i in range(1, K + 1):
            # calculate corresponding element of summa block-matrix as matrix multiplication of C(i) and Y(K-i) block-matrices
            summa[0][0] += C_K[i][0][0] * Y_K[K - i][0][0] + C_K[i][0][1] * Y_K[K - i][1][0]
            summa[0][1] += C_K[i][0][0] * Y_K[K - i][0][1] + C_K[i][0][1] * Y_K[K - i][1][1]
            summa[1][0] += C_K[i][1][0] * Y_K[K - i][0][0] + C_K[i][1][1] * Y_K[K - i][1][0]
            summa[1][1] += C_K[i][1][0] * Y_K[K - i][0][1] + C_K[i][1][1] * Y_K[K - i][1][1]

        # calculate Y(K) block-matrix as matrix multiplication of -Y(0) and summa block-matrices, and append it to the list of Y(K) block-matrices
        Y_K.append(
            [
                [-Y_K[0][0][0] * summa[0][0] + -Y_K[0][0][1] * summa[1][0], -Y_K[0][0][0] * summa[0][1] + -Y_K[0][0][1] * summa[1][1]],
                [-Y_K[0][1][0] * summa[0][0] + -Y_K[0][1][1] * summa[1][0], -Y_K[0][1][0] * summa[0][1] + -Y_K[0][1][1] * summa[1][1]]
            ])

    # Create an empty list for Y_1(K) matrix discretes
    Y1_K = list()

    # Create an empty list for X_2(K) matrix discretes
    Y2_K = list()

    # For K in [0; K-1]
    for K in range(hyper_parameters["discretes_count"]):
        # take the element at (0, 0) of Y(K) block-matrix as Y_1(K) matrix discrete (according to the notation (17))
        Y1_K.append(Y_K[K][0][0])

        # take the element at (1, 0) of Y(K) block-matrix as Y_2(K) matrix discrete (according to the notation (17))
        Y2_K.append(Y_K[K][1][0])

    # endregion Y(K), Y_1(K), Y_2(K)

    # region Y_1(t), Y_2(t)

    # Create a SymPy matrix Y_1(t) nxn filled with 0s
    Y1_t = sp.zeros(n, n)

    # Create a SymPy matrix Y_1(t) nxn filled with 0s
    Y2_t = sp.zeros(n, n)

    # Restore the X_1(t) and X_2(t) matrices according to the Equation (21)
    for K in range(hyper_parameters["discretes_count"]):
        Y1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * Y1_K[K]
        Y2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** K * Y2_K[K]

    # Clean numerical noise from Y1(t) and Y2(t)
    Y1_t = clean_matrix(Y1_t, tolerance=1e-10)
    Y2_t = clean_matrix(Y2_t, tolerance=1e-10)

    # endregion Y_1(t), Y_2(t)

    # region A+(t)

    # Calculate the generalized inverse A+(t) matrix according to the Equation (11)
    y = Y1_t + sp.I * Y2_t
    a = real_matrix - sp.I * imaginary_matrix
    generalized_inverse = sp.expand(y * a.T)

    # Clean numerical noise from the final result
    generalized_inverse = clean_matrix(generalized_inverse, tolerance=1e-10)

    # endregion A+(t)

    # Create the dictionary of intermediate results to use in generating calculation steps
    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                C1_K = C1_matrix_discretes, C2_K = C2_matrix_discretes, Y1_K = Y1_K, Y2_K = Y2_K, Y1_t = Y1_t, Y2_t = Y2_t)

    return generalized_inverse, intermediate_results

    # endregion Body

# endregion Functions
