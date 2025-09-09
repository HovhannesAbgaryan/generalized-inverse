import numpy as np
import sympy as sp
# from sympy import Matrix

from ..utils.calculus import find_derivatives, compute_discretes
from ..utils.calculation_steps import get_numerical_analytical_steps

# def analytical_method(A: Matrix) -> Matrix:
#     """
#     Moore–Penrose Type III (right pseudoinverse for full row rank):
#         A⁺ = Aᴴ (A Aᴴ)⁻¹
#     """
#     AH = A.conjugate().T
#     return AH * (A * AH).inv()

def numerical_analytical_method(input_matrix, real_matrix, imaginary_matrix, hyper_parameters):
    m, n = sp.shape(real_matrix)

    # region Derivatives and discretes

    real_matrix_derives = find_derivatives(real_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])
    imaginary_matrix_derives = find_derivatives(imaginary_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])

    real_matrix_discretes = compute_discretes(real_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])
    imaginary_matrix_discretes = compute_discretes(imaginary_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])

    # endregion Derivatives and discretes

    # region X1(K), X2(K)

    a = sp.Matrix([
                    [real_matrix_discretes[0].T, imaginary_matrix_discretes[0].T],
                    [imaginary_matrix_discretes[0].T, -real_matrix_discretes[0].T]
                  ])
    x = a.pinv()

    X1_K = [x[0:m, 0:n].copy().T]
    X2_K = [-x[0:m, n:2 * n].copy().T]

    for k in range(1, hyper_parameters["discretes_count"]):
        summa = [np.zeros(shape=(m, m), dtype=np.int_), np.zeros(shape=(m, m), dtype=np.int_)]
        for i in range(k):
            # index1 = k - i if k - i < len(real_matrix_discretes) else len(real_matrix_discretes) - 1
            # index2 = k - i if k - i < len(imaginary_matrix_discretes) else len(imaginary_matrix_discretes) - 1

            summa[0] += (X1_K[i].T * real_matrix_discretes[k - i].T - X2_K[i].T * imaginary_matrix_discretes[k - i].T)
            summa[1] += (X1_K[i].T * imaginary_matrix_discretes[k - i].T + X2_K[i].T * real_matrix_discretes[k - i].T)

        x1 = -summa[0] * X1_K[0].T + summa[1] * X2_K[0].T
        X1_K.append(x1.T)

        x2 = summa[0] * X2_K[0].T + summa[1] * X1_K[0].T
        X2_K.append(-x2.T)

    # print(f"X1(K) = {X1_K}")
    # print(f"X2(K) = {X2_K}")

    # endregion X1(K), X2(K)

    # region X1(t), X2(t)

    X1_t = np.zeros(shape=(n, m), dtype=np.int_)
    X2_t = np.zeros(shape=(n, m), dtype=np.int_)
    for k in range(hyper_parameters["discretes_count"]):
        X1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * X1_K[k]
        X2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * X2_K[k]
    # print(f"X1(t) = {X1_t}")
    # print(f"X2(t) = {X2_t}")

    # endregion X1(t), X2(t)

    # region A+(t)

    A_pseudo_inverse = X1_t + sp.I * X2_t
    # print(f"A+(t) = {A_pseudo_inverse}")

    # endregion A+(t)

    # region Calculation steps

    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                X1_K = X1_K, X2_K = X2_K, X1_t = X1_t, X2_t = X2_t)
    numerical_analytical_steps = get_numerical_analytical_steps(input_matrix, real_matrix, imaginary_matrix, hyper_parameters,
                                                                intermediate_results, A_pseudo_inverse)

    # endregion Calculation steps

    return A_pseudo_inverse, numerical_analytical_steps
