import sympy as sp

def clean_expression(expr, tolerance=1e-10):
    # region Summary
    """
    Recursively clean an expression by removing numerical noise.
    Sets coefficients smaller than tolerance to 0.
    """
    # endregion Summary

    # region Body

    if isinstance(expr, (int, float, complex)):
        if abs(expr) < tolerance:
            return 0
        return expr

    if isinstance(expr, sp.Basic):
        try:
            expr = sp.expand(expr)
            expr = expr.replace(
                lambda x: isinstance(x, (sp.Float, sp.Number))
                and abs(complex(x)) < tolerance,
                lambda x: sp.S.Zero,
            )
            expr = sp.nsimplify(expr, rational=False, tolerance=tolerance)
            expr = sp.simplify(expr)
            return expr
        except:
            return expr
    return expr

    # endregion Body

def clean_matrix(matrix, tolerance=1e-10):
    # region Summary
    """
    Clean all elements of a SymPy matrix by removing numerical noise.
    """
    # endregion Summary

    # region Body

    cleaned = sp.zeros(*matrix.shape)

    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            cleaned[i, j] = clean_expression(matrix[i, j], tolerance)

    return cleaned

    # endregion Body
