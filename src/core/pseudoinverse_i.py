import numpy as np
import sympy as sp

from ..utils.calculus import find_derivatives, compute_discretes
from ..utils.calculation_steps import get_analytical_steps, get_numerical_analytical_steps

def analytical_method(input_matrix, real_matrix, imaginary_matrix):
    # region B1(t), B2(t), B(t)

    B1_t = real_matrix * real_matrix.T + imaginary_matrix * imaginary_matrix.T
    B2_t = imaginary_matrix * real_matrix.T - real_matrix * imaginary_matrix.T
    B_t = B1_t + B2_t * sp.I

    # endregion B1(t), B2(t), B(t)

    # region X(t), X1(t), X2(t)

    X_t = sp.expand(B_t.pinv())
    X1_t, X2_t = X_t.as_real_imag()

    # endregion X(t), X1(t), X2(t)

    # region A+(t)

    real = real_matrix.T * X1_t + imaginary_matrix.T * X2_t
    imaginary = sp.expand(real_matrix.T * X2_t - imaginary_matrix.T * X1_t)
    A_pseudo_inverse = real + imaginary * sp.I

    # endregion A+(t)

    # region Calculation steps

    intermediate_results = dict(B1_t=B1_t, B2_t=B2_t, X1_t=X1_t, X2_t=X2_t)
    analytical_steps = get_analytical_steps(input_matrix, real_matrix, imaginary_matrix, intermediate_results, A_pseudo_inverse)

    # endregion Calculation steps

    return A_pseudo_inverse, analytical_steps

def numerical_analytical_method(input_matrix, real_matrix, imaginary_matrix, hyper_parameters):
    m = sp.shape(real_matrix)[0]

    # region Derivatives and discretes

    real_matrix_derives = find_derivatives(real_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])
    imaginary_matrix_derives = find_derivatives(imaginary_matrix, hyper_parameters["variable"], hyper_parameters["discretes_count"])

    real_matrix_discretes = compute_discretes(real_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])
    imaginary_matrix_discretes = compute_discretes(imaginary_matrix_derives, hyper_parameters["variable"], hyper_parameters["scaling_coefficient"], hyper_parameters["approximation_center"])

    # endregion Derivatives and discretes

    # region B1(K), B2(K), B(K)

    B1_K = list()
    B2_K = list()
    # K = max(len(real_matrix_discretes), len(imaginary_matrix_discretes))
    for k in range(hyper_parameters["discretes_count"]): # + 1
        B1_k = np.zeros(shape=(m, m), dtype=np.int_)
        B2_k = np.zeros(shape=(m, m), dtype=np.int_)
        for i in range(k + 1):
            # index1_1 = i if i < len(real_matrix_discretes) else len(real_matrix_discretes) - 1
            # index1_2 = k - i if k - i < len(real_matrix_discretes) else len(real_matrix_discretes) - 1
            # index2_1 = i if i < len(imaginary_matrix_discretes) else len(imaginary_matrix_discretes) - 1
            # index2_2 = k - i if k - i < len(imaginary_matrix_discretes) else len(imaginary_matrix_discretes) - 1

            B1_k += (real_matrix_discretes[i] * real_matrix_discretes[k - i].T +
                     imaginary_matrix_discretes[i] * imaginary_matrix_discretes[k - i].T)
            B2_k += (imaginary_matrix_discretes[i] * real_matrix_discretes[k - i].T -
                     real_matrix_discretes[i] * imaginary_matrix_discretes[k - i].T)

        B1_K.append(B1_k)
        B2_K.append(B2_k)

    # print(f"B1(K) = {B1_K}")
    # print(f"B2(K) = {B2_K}")

    B_K = list(())
    for k in range(hyper_parameters["discretes_count"]): # + 1
        B_K.append([
            [B1_K[k], -B2_K[k]],
            [B2_K[k], B1_K[k]]
        ])

    # endregion B1(K), B2(K), B(K)

    # region X(K), X1(K), X2(K)

    X_K = list(([
                    [B1_K[0].pinv(), -B2_K[0].pinv()],
                    [B2_K[0].pinv(), B1_K[0].pinv()]
                ],
    ))
    for k in range(1, hyper_parameters["discretes_count"]): # + 1
        summa = [
            [np.zeros(shape=(m, m), dtype=np.int_), np.zeros(shape=(m, m), dtype=np.int_)],
            [np.zeros(shape=(m, m), dtype=np.int_), np.zeros(shape=(m, m), dtype=np.int_)]
        ]
        for i in range(1, k + 1):
            summa[0][0] += B_K[i][0][0] * X_K[k - i][0][0] + B_K[i][0][1] * X_K[k - i][1][0]
            summa[0][1] += B_K[i][0][0] * X_K[k - i][0][1] + B_K[i][0][1] * X_K[k - i][1][1]
            summa[1][0] += B_K[i][1][0] * X_K[k - i][0][0] + B_K[i][1][1] * X_K[k - i][1][0]
            summa[1][1] += B_K[i][1][0] * X_K[k - i][0][1] + B_K[i][1][1] * X_K[k - i][1][1]
        X_K.append(
            [
                [-B1_K[0].pinv() * summa[0][0] + B2_K[0].pinv() * summa[1][0],
                 -B1_K[0].pinv() * summa[0][1] + B2_K[0].pinv() * summa[1][1]],
                [-B2_K[0].pinv() * summa[0][0] + -B1_K[0].pinv() * summa[1][0],
                 -B2_K[0].pinv() * summa[0][1] + -B1_K[0].pinv() * summa[1][1]]
            ])
    # print(f"X(K) = {X_K}")

    X1_K = list()
    X2_K = list()
    for k in range(hyper_parameters["discretes_count"]): # + 1
        X1_K.append(X_K[k][0][0])
        X2_K.append(X_K[k][1][0])
    # print(f"X1(K) = {X1_K}")
    # print(f"X2(K) = {X2_K}")

    # endregion X(K), X1(K), X2(K)

    # region X1(t), X2(t)

    X1_t = np.zeros(shape=(m, m), dtype=np.int_)
    X2_t = np.zeros(shape=(m, m), dtype=np.int_)
    for k in range(hyper_parameters["discretes_count"]): # + 1
        X1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * X1_K[k]
        X2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * X2_K[k]
    # print(f"X1(t) = {X1_t}")
    # print(f"X2(t) = {X2_t}")

    # endregion X1(t), X2(t)

    # region A+(t)

    a = real_matrix - sp.I * imaginary_matrix
    x = X1_t + sp.I * X2_t
    A_pseudo_inverse = sp.expand(a.T * x)
    # print(f"A+(t) = {A_pseudo_inverse}")

    # endregion A+(t)

    # region Calculation steps

    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                B1_K = B1_K, B2_K = B2_K, X1_K = X1_K, X2_K = X2_K, X1_t = X1_t, X2_t = X2_t)
    numerical_analytical_steps = get_numerical_analytical_steps(input_matrix, real_matrix, imaginary_matrix, hyper_parameters,
                                                                intermediate_results, A_pseudo_inverse)

    # endregion Calculation steps

    return A_pseudo_inverse, numerical_analytical_steps