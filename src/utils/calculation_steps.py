import sympy as sp
from .rounding import round_matrix, round_floats_in_expr

def matrix_to_text(matrix: sp.Matrix, ndigits: int = 4, evalf_symbolics: bool = False) -> str:
    # region Summary
    """
    Render a Sympy Matrix in textbook multi-line square-bracket form.
    - Rounds numeric entries using round_matrix(M, ndigits).
    - Also rounds Float atoms inside symbolic expressions.
    - If evalf_symbolics=True, performs M = M.evalf() before rounding (converts symbolic numeric
      expressions to floating approximations) — OFF by default to preserve symbolic t.
    Return example:
      [
        [ a, b, c ],
        [ d, e, f ]
      ]
    """
    # endregion Summary

    # region Body

    try:
        if evalf_symbolics:
            M_proc = matrix.evalf()
        else:
            M_proc = matrix
    except Exception:
        M_proc = matrix

    try:
        M_rounded = round_matrix(M_proc, ndigits)
    except Exception:
        M_rounded = M_proc

    row_strs = []
    for row in M_rounded.tolist():
        elems = []
        for el in row:
            try:
                el2 = round_floats_in_expr(el, ndigits)
                elems.append(sp.sstr(el2))
            except Exception:
                elems.append(str(el))
        row_strs.append("[ " + ", ".join(elems) + " ]")

    if not row_strs:
        return "[ ]"

    text_lines = ["["]
    for i, r in enumerate(row_strs):
        comma = "," if i < len(row_strs) - 1 else ""
        text_lines.append("  " + r + comma)
    text_lines.append("]")

    return "\n".join(text_lines)

    # endregion Body


def get_analytical_steps(input_matrix: sp.Matrix, real_matrix: sp.Matrix, imaginary_matrix: sp.Matrix,
                         method_name: str, intermediate_results: dict, generalized_inverse) -> list[str]:
    # region Summary
    """
    :param input_matrix: Input matrix (denoted as A(t))
    :param real_matrix: Real part of input matrix (denoted as A_1(t))
    :param imaginary_matrix: Imaginary part of input matrix (denoted as A_2(t))
    :param method_name: Method name (Moore-Penrose I, II, III, or IV)
    :param intermediate_results: Calculations' intermediate results
    :param generalized_inverse: Generalized inverse matrix (denoted as A+(t))
    """
    # endregion Summary

    # region Body

    steps = [
             # Original matrix
             f"A(t) = \n{matrix_to_text(input_matrix)}",

             # Real and imaginary parts
             f"A₁(t) = \n{matrix_to_text(real_matrix)}", f"A₂(t) = \n{matrix_to_text(imaginary_matrix)}",

             f"\n{method_name}\n"
    ]

    # region Moore-Penrose I

    if "B1_t" in intermediate_results.keys():
        steps.append(f"B₁(t) = \n{matrix_to_text(intermediate_results['B1_t'])}")

    if "B2_t" in intermediate_results.keys():
        steps.append(f"B₂(t) = \n{matrix_to_text(intermediate_results['B2_t'])}")

    if "X1_t" in intermediate_results.keys():
        steps.append(f"X₁(t) = \n{matrix_to_text(intermediate_results['X1_t'])}")

    if "X2_t" in intermediate_results.keys():
        steps.append(f"X₂(t) = \n{matrix_to_text(intermediate_results['X2_t'])}")

    # endregion Moore-Penrose I

    # region Moore-Penrose II

    if "C1_t" in intermediate_results.keys():
        steps.append(f"C₁(t) = \n{matrix_to_text(intermediate_results['C1_t'])}")

    if "C2_t" in intermediate_results.keys():
        steps.append(f"C₂(t) = \n{matrix_to_text(intermediate_results['C2_t'])}")

    if "Y1_t" in intermediate_results.keys():
        steps.append(f"Y₁(t) = \n{matrix_to_text(intermediate_results['Y1_t'])}")

    if "Y2_t" in intermediate_results.keys():
        steps.append(f"Y₂(t) = \n{matrix_to_text(intermediate_results['Y2_t'])}")

    # endregion Moore-Penrose II

    # Final A⁺(t)
    steps.append(f"A⁺(t) = \n{matrix_to_text(generalized_inverse)}")

    return steps

    # endregion Body

def get_numerical_analytical_steps(input_matrix: sp.Matrix, real_matrix: sp.Matrix, imaginary_matrix: sp.Matrix,
                                   hyper_parameters: dict, intermediate_results: dict, generalized_inverse) -> list[str]:
    # region Summary
    """
    :param input_matrix: Input matrix (denoted as A(t))
    :param real_matrix: Real part of input matrix (denoted as A_1(t))
    :param imaginary_matrix: Imaginary part of input matrix (denoted as A_2(t))
    :param hyper_parameters: Hyper-parameters for numerical-analytical method (variable, discretes count (denoted as K),
                                                                               approximation center (denoted as t_nyu), scaling coefficient (denoted as H))
    :param intermediate_results: Calculations' intermediate results
    :param generalized_inverse: Generalized inverse matrix (denoted as A+(t))
    """
    # endregion Summary

    # region Body

    steps = [
        # Original matrix
        f"A(t) = \n{matrix_to_text(input_matrix)}",

        # Real and imaginary parts
        f"A₁(t) = \n{matrix_to_text(real_matrix)}", f"A₂(t) = \n{matrix_to_text(imaginary_matrix)}",
        
        # Hyper-parameters
        f"\nK = {hyper_parameters['discretes_count']}, t = {hyper_parameters['approximation_center']}, H = {hyper_parameters['scaling_coefficient']}; {hyper_parameters['method']}\n"
    ]

    for K in range(hyper_parameters["discretes_count"]):
        steps.append(f"K = {K}")
        steps.append(f"A₁({K}) = \n{matrix_to_text(intermediate_results['real_matrix_discretes'][K])}")
        steps.append(f"A₂({K}) = \n{matrix_to_text(intermediate_results['imaginary_matrix_discretes'][K])}")

    # region Moore-Penrose I

    if "B1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]):
            steps.append(f"K = {K}")
            steps.append(f"B₁({K}) = \n{matrix_to_text(intermediate_results['B1_K'][K])}")
            steps.append(f"B₂({K}) = \n{matrix_to_text(intermediate_results['B2_K'][K])}")

    # region Moore-Penrose III, IV

    if "X1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]):
            steps.append(f"K = {K}")
            steps.append(f"X₁({K}) = \n{matrix_to_text(intermediate_results['X1_K'][K])}")
            steps.append(f"X₂({K}) = \n{matrix_to_text(intermediate_results['X2_K'][K])}")

    if "X1_t" in intermediate_results.keys():
        steps.append(f"X₁(t) = \n{matrix_to_text(intermediate_results['X1_t'])}")
        steps.append(f"X₂(t) = \n{matrix_to_text(intermediate_results['X2_t'])}")

    # endregion Moore-Penrose III, IV

    # endregion Moore-Penrose I

    # region Moore-Penrose II

    if "C1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]):
            steps.append(f"K = {K}")
            steps.append(f"C₁({K}) = \n{matrix_to_text(intermediate_results['C1_K'][K])}")
            steps.append(f"C₂({K}) = \n{matrix_to_text(intermediate_results['C2_K'][K])}")

    if "Y1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]):
            steps.append(f"K = {K}")
            steps.append(f"Y₁({K}) = \n{matrix_to_text(intermediate_results['Y1_K'][K])}")
            steps.append(f"Y₂({K}) = \n{matrix_to_text(intermediate_results['Y2_K'][K])}")

    if "Y1_t" in intermediate_results.keys():
        steps.append(f"Y₁(t) = \n{matrix_to_text(intermediate_results['Y1_t'])}")
        steps.append(f"Y₂(t) = \n{matrix_to_text(intermediate_results['Y2_t'])}")

    # endregion Moore-Penrose II

    # Final A⁺(t)
    steps.append(f"A⁺(t) = \n{matrix_to_text(generalized_inverse)}")

    return steps

    # endregion Body
