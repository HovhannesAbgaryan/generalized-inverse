from sympy import Matrix

from . import pseudoinverse_i, pseudoinverse_ii, pseudoinverse_iii, pseudoinverse_iv

# def pinv_type_I(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
#     rows, columns = sizes
#     if rows > columns:
#         raise ValueError("Matrix sizes must be: rows <= columns")
#
#     real_matrix, imaginary_matrix = matrix.as_real_imag()
#
#     if hyper_parameters["use_analytical_method"]:
#         pseudo_inverse, steps = pseudoinverse_i.analytical_method(matrix, real_matrix, imaginary_matrix)
#     else:
#         pseudo_inverse, steps = pseudoinverse_i.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)
#
#     return pseudo_inverse, steps
#
# def pinv_type_II(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
#     rows, columns = sizes
#     if rows < columns:
#         raise ValueError("Matrix sizes must be: rows >= columns")
#
#     real_matrix, imaginary_matrix = matrix.as_real_imag()
#
#     if hyper_parameters["use_analytical_method"]:
#         pseudo_inverse, steps = pseudoinverse_ii.analytical_method(matrix, real_matrix, imaginary_matrix)
#     else:
#         pseudo_inverse, steps = pseudoinverse_ii.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)
#
#     return pseudo_inverse, steps

def pinv_type_I_II(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    rows, columns = sizes

    real_matrix, imaginary_matrix = matrix.as_real_imag()

    if rows <= columns:
        if hyper_parameters["use_analytical_method"]:
            pseudo_inverse, steps = pseudoinverse_i.analytical_method(matrix, real_matrix, imaginary_matrix)
        else:
            pseudo_inverse, steps = pseudoinverse_i.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)
    else:
        if hyper_parameters["use_analytical_method"]:
            pseudo_inverse, steps = pseudoinverse_ii.analytical_method(matrix, real_matrix, imaginary_matrix)
        else:
            pseudo_inverse, steps = pseudoinverse_ii.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)

    return pseudo_inverse, steps

def pinv_type_III(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    real_matrix, imaginary_matrix = matrix.as_real_imag()

    pseudo_inverse, steps = pseudoinverse_iii.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)

    return pseudo_inverse, steps

def pinv_type_IV(sizes: tuple, hyper_parameters: dict, matrix: Matrix):
    real_matrix, imaginary_matrix = matrix.as_real_imag()

    pseudo_inverse, steps = pseudoinverse_iv.numerical_analytical_method(matrix, real_matrix, imaginary_matrix, hyper_parameters)

    return pseudo_inverse, steps
