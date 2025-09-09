import sympy as sp

def matrix_to_text(M: sp.Matrix) -> str:
    """
    Render a Sympy Matrix M in textbook-style square-bracket form.
    E.g.:
      [ [a, b],
        [c, d] ]
    """
    # Convert each row of M into a comma-separated list
    row_strs = []
    for row in M.tolist():
        # Convert each element to its Sympy string (maintains t, I, etc.)
        elems = [sp.sstr(el) for el in row]
        row_strs.append("[ " + ", ".join(elems) + " ]")

    # Join the rows, indenting second and subsequent rows
    if not row_strs:
        return "[ ]"

    # Build the full block
    text = "[ " + row_strs[0] + "\n"
    for r in row_strs[1:]:
        text += "  " + r + "\n"
    text += "]"
    return text

def get_analytical_steps(input_matrix: sp.Matrix, real_matrix: sp.Matrix, imaginary_matrix: sp.Matrix,
                         intermediate_results: dict, pseudo_inverse) -> list[str]:

    steps = [
             # Original matrix
             f"A(t) = \n{matrix_to_text(input_matrix)}",

             # Real and imaginary parts
             f"A₁(t) = \n{matrix_to_text(real_matrix)}", f"A₂(t) = \n{matrix_to_text(imaginary_matrix)}"
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
    steps.append(f"A⁺(t) = \n{matrix_to_text(pseudo_inverse)}")

    return steps

def get_numerical_analytical_steps(input_matrix: sp.Matrix, real_matrix: sp.Matrix, imaginary_matrix: sp.Matrix,
                                   hyper_parameters: dict, intermediate_results: dict, pseudo_inverse) -> list[str]:
    steps = [
        # Original matrix
        f"A(t) = \n{matrix_to_text(input_matrix)}",

        # Real and imaginary parts
        f"A₁(t) = \n{matrix_to_text(real_matrix)}", f"A₂(t) = \n{matrix_to_text(imaginary_matrix)}",
        
        # Hyper-parameters
        f"\nK = {hyper_parameters['discretes_count']}, t = {hyper_parameters['approximation_center']}, H = {hyper_parameters['scaling_coefficient']}\n"
    ]

    for K in range(hyper_parameters["discretes_count"]):
        steps.append(f"K = {K}")
        steps.append(f"A₁({K}) = \n{matrix_to_text(intermediate_results['real_matrix_discretes'][K])}")
        steps.append(f"A₂({K}) = \n{matrix_to_text(intermediate_results['imaginary_matrix_discretes'][K])}")

    # region Moore-Penrose I

    if "B1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]): # + 1
            steps.append(f"K = {K}")
            steps.append(f"B₁({K}) = \n{matrix_to_text(intermediate_results['B1_K'][K])}")
            steps.append(f"B₂({K}) = \n{matrix_to_text(intermediate_results['B2_K'][K])}")

    # region Moore-Penrose III

    if "X1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"]): # + 1
            steps.append(f"K = {K}")
            steps.append(f"X₁({K}) = \n{matrix_to_text(intermediate_results['X1_K'][K])}")
            steps.append(f"X₂({K}) = \n{matrix_to_text(intermediate_results['X2_K'][K])}")

    if "X1_t" in intermediate_results.keys():
        steps.append(f"X₁(t) = \n{matrix_to_text(intermediate_results['X1_t'])}")
        steps.append(f"X₂(t) = \n{matrix_to_text(intermediate_results['X2_t'])}")

    # endregion Moore-Penrose III

    # endregion Moore-Penrose I

    # region Moore-Penrose II

    if "C1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"] + 1):
            steps.append(f"K = {K}")
            steps.append(f"C₁({K}) = \n{matrix_to_text(intermediate_results['C1_K'][K])}")
            steps.append(f"C₂({K}) = \n{matrix_to_text(intermediate_results['C2_K'][K])}")

    if "Y1_K" in intermediate_results.keys():
        for K in range(hyper_parameters["discretes_count"] + 1):
            steps.append(f"K = {K}")
            steps.append(f"Y₁({K}) = \n{matrix_to_text(intermediate_results['Y1_K'][K])}")
            steps.append(f"Y₂({K}) = \n{matrix_to_text(intermediate_results['Y2_K'][K])}")

    if "Y1_t" in intermediate_results.keys():
        steps.append(f"Y₁(t) = \n{matrix_to_text(intermediate_results['Y1_t'])}")
        steps.append(f"Y₂(t) = \n{matrix_to_text(intermediate_results['Y2_t'])}")

    # endregion Moore-Penrose II

    # Final A⁺(t)
    steps.append(f"A⁺(t) = \n{matrix_to_text(pseudo_inverse)}")

    return steps