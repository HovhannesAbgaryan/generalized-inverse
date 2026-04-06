# region Summary
"""
Symbolic-first error computation for Moore-Penrose conditions.

- Builds symbolic Frobenius-norm expressions for each of the 4 Moore-Penrose conditions once (symbolic work).
- Then evaluates those expressions at a small set of numeric t test points.
- Returns a dict-of-dicts:
    {
        t1: {'c1': float, 'c2': float, 'c3': float, 'c4': float},
        t2: {'c1': float, 'c2': float, 'c3': float, 'c4': float},
        t3: {'c1': float, 'c2': float, 'c3': float, 'c4': float}
    }
  or None on a fatal error.
"""
# endregion Summary

import math
import sympy as sp

# Symbol used for parameter
t = sp.Symbol('t', real=True)

def frobenius_norm_symbolic(matrix: sp.Matrix) -> sp.Expr:
    # region Summary
    """
    Return a symbolic expression for the Frobenius norm of a matrix.
    Norm = sqrt(sum(elem * conjugate(elem))).
    `matrix` should be a SymPy Matrix-like object.
    """
    # endregion Summary

    # region Body

    total = sp.Integer(0)
    # iterate rows/cols to be robust
    rows = matrix.rows
    cols = matrix.cols
    for i in range(rows):
        for j in range(cols):
            elem = matrix[i, j]
            total += sp.simplify(elem * sp.conjugate(elem))
    return sp.sqrt(sp.simplify(total))

    # endregion Body

# region Moore-Penrose Condition Norms

def norm_expr_condition_1(A: sp.Matrix, A_plus: sp.Matrix) -> sp.Expr:
    """Symbolic expression for Frobenius norm of (A·A⁺·A - A)."""
    diff = sp.simplify((A * A_plus * A) - A)
    return sp.simplify(frobenius_norm_symbolic(diff))


def norm_expr_condition_2(A: sp.Matrix, A_plus: sp.Matrix) -> sp.Expr:
    """Symbolic expression for Frobenius norm of (A⁺·A·A⁺ - A⁺)."""
    diff = sp.simplify((A_plus * A * A_plus) - A_plus)
    return sp.simplify(frobenius_norm_symbolic(diff))


def norm_expr_condition_3(A: sp.Matrix, A_plus: sp.Matrix) -> sp.Expr:
    """Symbolic expression for Frobenius norm of (A·A⁺ - (A·A⁺).H)."""
    AAp = A * A_plus
    diff = sp.simplify(AAp - AAp.H)
    return sp.simplify(frobenius_norm_symbolic(diff))


def norm_expr_condition_4(A: sp.Matrix, A_plus: sp.Matrix) -> sp.Expr:
    """Symbolic expression for Frobenius norm of (A⁺·A - (A⁺·A).H)."""
    ApA = A_plus * A
    diff = sp.simplify(ApA - ApA.H)
    return sp.simplify(frobenius_norm_symbolic(diff))

# endregion Moore-Penrose Condition Norms

def _make_numeric_evaluator(expr: sp.Expr):
    # region Summary
    """
    Try to create a fast numeric evaluator for `expr` with one variable `t`.
    Prefer numpy backend; fall back to math backend via lambdify,
    and as a final safety net we will use symbolic substitution + evalf.
    Returns a callable f(t_val) -> float or raises if lambdify creation fails.
    """
    # endregion Summary

    # region Body

    try:
        # Prefer numpy (fast); if numpy is absent, this will raise ImportError
        import numpy  # noqa: F401
        f = sp.lambdify(t, expr, "numpy")
        return f, "numpy"
    except Exception:
        try:
            # Fallback to math (pure python math module)
            f = sp.lambdify(t, expr, "math")
            return f, "math"
        except Exception:
            # Signal that lambdify wasn't created — caller must fall back to subs+evalf
            return None, None

    # endregion Body

def _safe_eval_expr(expr_sym: sp.Expr, evaluator_func, t_val):
    # region Summary
    """
    Try to safely evaluate expr_sym at t_val.
    - evaluator_func: callable(t_val) -> numeric (or None if not available)
    - expr_sym: SymPy expression (fallback)
    Returns float numeric or raises Exception if both attempts failed.
    """
    # endregion Summary

    # region Body

    # 1) Try evaluator_func (lambdified), if provided
    if evaluator_func is not None:
        try:
            raw = evaluator_func(t_val)
            # numpy scalars have .item()
            if hasattr(raw, "item"):
                raw = raw.item()
            # Complex with tiny imag part -> accept real part
            if isinstance(raw, complex):
                if abs(raw.imag) < 1e-12:
                    raw = raw.real
                else:
                    raise ValueError("Complex result with non-negligible imaginary part")
            # Must be finite
            valf = float(raw)
            if not math.isfinite(valf):
                raise ValueError("Non-finite result from lambdify")
            return valf
        except Exception:
            # fall through to symbolic fallback
            pass

    # 2) Symbolic fallback
    try:
        val_sub = expr_sym.subs(t, t_val)
        val_num = sp.N(val_sub)
        # val_num might be a sympy complex, handle similarly
        if getattr(val_num, "is_real", None) is False:
            # try to cast to complex and accept tiny imaginary part
            cre = complex(val_num)
            if abs(cre.imag) < 1e-12:
                valf = float(cre.real)
            else:
                raise ValueError("Complex sympy numeric")
        else:
            valf = float(val_num)
        if not math.isfinite(valf):
            raise ValueError("Non-finite result from sympy N")
        return valf
    except Exception as e:
        raise

    # endregion Body

def calculate_errors(input_matrix: sp.Matrix, generalized_inverse: sp.Matrix, hyper_parameters: dict, use_lambdify: bool = True):
    # region Summary
    """
    Robust calculate_errors: build symbolic expressions once, then evaluate safely.
    Returns dict-of-dicts or None on fatal error.
    """
    # endregion Summary

    # region Body

    try:
        center = hyper_parameters.get("approximation_center", 0)
        test_points = [center - 0.1, center, center + 0.1]

        # Build symbolic norm expressions (reuse previously defined functions)
        expr_c1 = norm_expr_condition_1(input_matrix, generalized_inverse)
        expr_c2 = norm_expr_condition_2(input_matrix, generalized_inverse)
        expr_c3 = norm_expr_condition_3(input_matrix, generalized_inverse)
        expr_c4 = norm_expr_condition_4(input_matrix, generalized_inverse)

        # Try to make lambdify functions (may be None)
        f_c1, _ = _make_numeric_evaluator(expr_c1) if use_lambdify else (None, None)
        f_c2, _ = _make_numeric_evaluator(expr_c2) if use_lambdify else (None, None)
        f_c3, _ = _make_numeric_evaluator(expr_c3) if use_lambdify else (None, None)
        f_c4, _ = _make_numeric_evaluator(expr_c4) if use_lambdify else (None, None)

        errors_dict = {}
        for t_val in test_points:
            try:
                c1 = _safe_eval_expr(expr_c1, f_c1, t_val)
            except Exception:
                c1 = float('inf')

            try:
                c2 = _safe_eval_expr(expr_c2, f_c2, t_val)
            except Exception:
                c2 = float('inf')

            try:
                c3 = _safe_eval_expr(expr_c3, f_c3, t_val)
            except Exception:
                c3 = float('inf')

            try:
                c4 = _safe_eval_expr(expr_c4, f_c4, t_val)
            except Exception:
                c4 = float('inf')

            try:
                key = float(t_val)
            except Exception:
                key = str(t_val)

            errors_dict[key] = {'c1': c1, 'c2': c2, 'c3': c3, 'c4': c4}

        return errors_dict

    except Exception:
        return None

    # endregion Body
