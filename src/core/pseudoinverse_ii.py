import numpy as np
import sympy as sp

from ..utils.calculus import find_derivatives, compute_discretes
from ..utils.calculation_steps import get_analytical_steps, get_numerical_analytical_steps

def analytical_method(input_matrix, real_matrix, imaginary_matrix):
    # region C1(t), C2(t), C(t)

    C1_t = real_matrix.T * real_matrix + imaginary_matrix.T * imaginary_matrix
    C2_t = real_matrix.T * imaginary_matrix - imaginary_matrix.T * real_matrix
    C_t = C1_t + C2_t * sp.I

    # endregion C1(t), C2(t), C(t)

    # region Y(t), Y1(t), Y2(t)

    Y_t = sp.expand(C_t.pinv())
    Y1_t, Y2_t = Y_t.as_real_imag()

    # endregion Y(t), Y1(t), Y2(t)

    # region A+(t)

    real = Y1_t * real_matrix.T + Y2_t * imaginary_matrix.T
    imaginary = sp.expand(Y2_t * real_matrix.T - Y1_t * imaginary_matrix.T)
    A_pseudo_inverse = real + imaginary * sp.I

    # endregion A+(t)

    # region Calculation steps

    intermediate_results = dict(C1_t = C1_t, C2_t = C2_t, Y1_t = Y1_t, Y2_t = Y2_t)
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

    # region C1(K), C2(K), C(K)

    C1_K = list()
    C2_K = list()
    # K = max(len(real_matrix_discretes), len(imaginary_matrix_discretes))
    for k in range(hyper_parameters["discretes_count"] + 1):
        C1_k = np.zeros(shape=(m, m), dtype=np.int_)
        C2_k = np.zeros(shape=(m, m), dtype=np.int_)
        for i in range(k + 1):
            index1_1 = i if i < len(real_matrix_discretes) else len(real_matrix_discretes) - 1
            index1_2 = k - i if k - i < len(real_matrix_discretes) else len(real_matrix_discretes) - 1
            index2_1 = i if i < len(imaginary_matrix_discretes) else len(imaginary_matrix_discretes) - 1
            index2_2 = k - i if k - i < len(imaginary_matrix_discretes) else len(imaginary_matrix_discretes) - 1
            C1_k += (real_matrix_discretes[index1_1] * real_matrix_discretes[index1_2].T +
                     imaginary_matrix_discretes[index2_1] * imaginary_matrix_discretes[index2_2].T)
            C2_k += (imaginary_matrix_discretes[index2_1] * real_matrix_discretes[index1_2].T -
                     real_matrix_discretes[index1_1] * imaginary_matrix_discretes[index2_2].T)
        C1_K.append(C1_k)
        C2_K.append(C2_k)
    # print(f"C1(K) = {C1_K}")
    # print(f"C2(K) = {C2_K}")

    C_K = list(())
    for k in range(hyper_parameters["discretes_count"] + 1):
        C_K.append([
            [C1_K[k], -C2_K[k]],
            [C2_K[k], C1_K[k]]
        ])

    # endregion C1(K), C2(K), C(K)

    # region Y(K), Y1(K), Y2(K)

    Y_K = list(([
                    [C1_K[0].pinv(), -C2_K[0].pinv()],
                    [C2_K[0].pinv(), C1_K[0].pinv()]
                ],
    ))
    for k in range(1, hyper_parameters["discretes_count"] + 1):
        summa = [
            [np.zeros(shape=(m, m), dtype=np.int_), np.zeros(shape=(m, m), dtype=np.int_)],
            [np.zeros(shape=(m, m), dtype=np.int_), np.zeros(shape=(m, m), dtype=np.int_)]
        ]
        for i in range(1, k + 1):
            summa[0][0] += C_K[i][0][0] * Y_K[k - i][0][0] + C_K[i][0][1] * Y_K[k - i][1][0]
            summa[0][1] += C_K[i][0][0] * Y_K[k - i][0][1] + C_K[i][0][1] * Y_K[k - i][1][1]
            summa[1][0] += C_K[i][1][0] * Y_K[k - i][0][0] + C_K[i][1][1] * Y_K[k - i][1][0]
            summa[1][1] += C_K[i][1][0] * Y_K[k - i][0][1] + C_K[i][1][1] * Y_K[k - i][1][1]
        Y_K.append(
            [
                [-C1_K[0].pinv() * summa[0][0] + C2_K[0].pinv() * summa[1][0],
                 -C1_K[0].pinv() * summa[0][1] + C2_K[0].pinv() * summa[1][1]],
                [-C2_K[0].pinv() * summa[0][0] + -C1_K[0].pinv() * summa[1][0],
                 -C2_K[0].pinv() * summa[0][1] + -C1_K[0].pinv() * summa[1][1]]
            ])
    # print(f"Y(K) = {Y_K}")

    Y1_K = list()
    Y2_K = list()
    for k in range(hyper_parameters["discretes_count"] + 1):
        Y1_K.append(Y_K[k][0][0])
        Y2_K.append(Y_K[k][1][0])
    # print(f"Y1(K) = {Y1_K}")
    # print(f"Y2(K) = {Y2_K}")

    # endregion Y(K), Y1(K), Y2(K)

    # region Y1(t), Y2(t)

    Y1_t = np.zeros(shape=(m, m), dtype=np.int_)
    Y2_t = np.zeros(shape=(m, m), dtype=np.int_)
    for k in range(hyper_parameters["discretes_count"] + 1):
        Y1_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * Y1_K[k]
        Y2_t += ((hyper_parameters["variable"] - hyper_parameters["approximation_center"]) / hyper_parameters["scaling_coefficient"]) ** k * Y2_K[k]
    # print(f"Y1(t) = {Y1_t}")
    # print(f"Y2(t) = {Y2_t}")

    # endregion Y1(t), Y2(t)

    # region A+(t)

    a = real_matrix - sp.I * imaginary_matrix
    y = Y1_t + sp.I * Y2_t
    A_pseudo_inverse = sp.expand(a.T * y)
    # print(f"A+(t) = {A_pseudo_inverse}")

    # endregion A+(t)

    # region Calculation steps

    intermediate_results = dict(real_matrix_discretes = real_matrix_discretes, imaginary_matrix_discretes = imaginary_matrix_discretes,
                                C1_K = C1_K, C2_K = C2_K, Y1_K = Y1_K, Y2_K = Y2_K, Y1_t = Y1_t, Y2_t = Y2_t)
    numerical_analytical_steps = get_numerical_analytical_steps(input_matrix, real_matrix, imaginary_matrix, hyper_parameters,
                                                                intermediate_results, A_pseudo_inverse)

    # endregion Calculation steps

    return A_pseudo_inverse, numerical_analytical_steps
