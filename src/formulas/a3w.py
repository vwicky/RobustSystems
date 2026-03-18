import sympy as sp
import numpy as np
from src.formulas.kh3w import get_K_G3W_functions

def get_a3W_functions():
    """
    Returns two functions for evaluating and displaying the a_3W formula.
    
    Returns:
        tuple: (compute_a3W_numpy, get_a3W_sympy)
    """
    
    def compute_a3W_numpy(k, t, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerically stable implementation via derivative of Q_3W:
            Q_3W(t) = 1 - K_Г3W(t)
            a_3W(t) = dQ_3W/dt

        Uses finite differences around t and clips tiny negative numerical noise.
        """
        compute_k_gamma, _ = get_K_G3W_functions()
        t_val = float(np.asarray(t, dtype=float))
        if t_val <= 0:
            raise ValueError("t must be positive for a_3W computation.")

        # Relative step keeps precision across small/large time scales.
        dt = max(1e-5, 1e-4 * t_val)
        t_minus = max(1e-12, t_val - dt)
        t_plus = t_val + dt
        actual_dt = t_plus - t_minus

        k_minus = float(
            compute_k_gamma(
                k=k,
                t=t_minus,
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
        k_plus = float(
            compute_k_gamma(
                k=k,
                t=t_plus,
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

        q_minus = 1.0 - k_minus
        q_plus = 1.0 - k_plus
        derivative = (q_plus - q_minus) / actual_dt
        return max(float(derivative), 0.0)


    def get_a3W_sympy():
        """
        Symbolic implementation aligned with numeric path:
            a_3W(t) = d/dt (1 - K_Г3W(k,t)).
        """
        k, t = sp.symbols('k t', real=True, positive=True)
        k_gamma_expr = get_K_G3W_functions()[1]()
        q_expr = 1 - k_gamma_expr
        return sp.diff(q_expr, t)

    return compute_a3W_numpy, get_a3W_sympy