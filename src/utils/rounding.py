import sympy as sp

def round_floats_in_expr(expr: sp.Expr, ndigits: int = 4) -> sp.Expr:
    # region Summary
    """
    Replace Float atoms inside a SymPy expression with rounded Float atoms.
    Keeps symbolic structure but shortens float coefficients.
    Example: -0.0925925925925926*t**2 -> -0.0926*t**2 (for ndigits=4)
    """
    # endregion Summary

    # region Body

    try:
        floats = list(expr.atoms(sp.Float))
        if not floats:
            return expr
        mapping = {}
        for f in floats:
            fval = float(f)
            rounded = round(fval, ndigits)
            mapping[f] = sp.Float(str(rounded))
        new_expr = expr.xreplace(mapping)
        return new_expr
    except Exception:
        return expr

    # endregion Body

def round_matrix(matrix: sp.Matrix, ndigits: int = 4) -> sp.Matrix:
    # region Summary
    """
    Round numeric entries of a Sympy Matrix to `ndigits` decimal places.
    Also rounds Float atoms inside symbolic expressions.
    Returns a new sympy.Matrix.
    """
    # endregion Summary

    # region Body

    if not isinstance(matrix, sp.Matrix):
        return matrix

    rows = []
    for row in matrix.tolist():
        new_row = []
        for el in row:
            # If the element contains symbols, keep symbolic but round floats inside
            try:
                if hasattr(el, "free_symbols") and len(el.free_symbols) > 0:
                    new_el = round_floats_in_expr(el, ndigits)
                    new_row.append(new_el)
                    continue
            except Exception:
                pass

            # Try to convert numeric types to Python complex/float and round parts
            try:
                num = sp.N(el, 15)
                val = complex(num)
                real_part = val.real
                imag_part = val.imag

                real_r = round(real_part, ndigits)
                imag_r = round(imag_part, ndigits)

                if imag_r == 0:
                    if float(real_r).is_integer():
                        new_el = int(real_r)
                    else:
                        new_el = float(f"{real_r:.{ndigits}f}")
                else:
                    new_el = complex(float(f"{real_r:.{ndigits}f}"), float(f"{imag_r:.{ndigits}f}"))

                sym_new = sp.sympify(new_el)
                new_row.append(sym_new)
            except Exception:
                # Fallback: try to round float atoms inside expression
                try:
                    new_el = round_floats_in_expr(el, ndigits)
                    new_row.append(new_el)
                except Exception:
                    new_row.append(el)
        rows.append(new_row)

    return sp.Matrix(rows)

    # endregion Body
