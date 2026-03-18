import sympy as sp
import numpy as np
import scipy.integrate as integrate
from src.formulas.p3w import get_P3W_functions

def get_T3W_functions():
    """
    Returns two functions for evaluating and displaying the T_3W formula.
    
    Returns:
        tuple: (compute_T3W_numpy, get_T3W_sympy)
    """
    compute_p3w, get_p3w_sympy = get_P3W_functions()

    def compute_T3W_numpy(x3, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerically stable implementation via direct integration:
        T_3W(x3) = \int_0^\infty P_3W(x3, t) dt.

        Using P_3W as the integrand avoids catastrophic cancellation that appears
        in the fully expanded alternating-sum form.
        """
        def integrand(t: float) -> float:
            return float(
                compute_p3w(
                    x3=x3,
                    t=t,
                    l0=l0,
                    l1=l1,
                    l2=l2,
                    l3=l3,
                    a1=a1,
                    a2=a2,
                    a3=a3,
                    b3=b3,
                )
            )

        integral_val, _ = integrate.quad(integrand, 0, np.inf, limit=300, epsabs=1e-10, epsrel=1e-8)
        return max(float(integral_val), 0.0)


    def get_T3W_sympy():
        """
        Symbolic implementation aligned with the numeric path:
        T_3W(x3) = Integral(P_3W(x3, t), (t, 0, oo)).
        """
        p3w_expr = get_p3w_sympy()
        t_symbol = next((sym for sym in p3w_expr.free_symbols if sym.name == "t"), None)
        if t_symbol is None:
            raise ValueError("Could not identify time symbol t in P_3W symbolic expression.")
        return sp.Integral(p3w_expr, (t_symbol, 0, sp.oo))

    return compute_T3W_numpy, get_T3W_sympy


def get_T_Gamma_3W_sympy():
    """
    Symbolic formula for T_Γ3W(k): mean time to failure with redundancy.
    T_Gamma_3W(k) = Sum(T_3W(x_3), (x_3, k, a_1 * a_2 * a_3))
    Returns a SymPy Eq for display/LaTeX.
    Note: this representation is intentionally display-oriented and does not
    provide a direct numeric evaluation path by itself.
    """
    k, x_3, a_1, a_2, a_3 = sp.symbols("k x_3 a_1 a_2 a_3", integer=True, nonnegative=True)
    T_Gamma_3W = sp.Function("T_{\\Gamma 3W}")
    T_3W = sp.Function("T_{3W}")
    right_side = sp.Sum(T_3W(x_3), (x_3, k, a_1 * a_2 * a_3))
    return sp.Eq(T_Gamma_3W(k), right_side)