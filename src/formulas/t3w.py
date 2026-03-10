import sympy as sp
import numpy as np
from scipy.special import comb
import scipy.integrate as integrate

def get_T3W_functions():
    """
    Returns two functions for evaluating and displaying the T_3W formula.
    
    Returns:
        tuple: (compute_T3W_numpy, get_T3W_sympy)
    """
    
    def compute_T3W_numpy(x3, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerical implementation using nested loops and scipy.integrate.quad.
        Returns a single scalar float value.
        """
        lower_limit_x2 = int(np.ceil(x3 / a3))
        lower_limit_x1 = int(np.ceil(lower_limit_x2 / a2))
        
        total_sum = 0.0
        
        for x1 in range(lower_limit_x1, a1 + 1):
            c_a1_x1 = comb(a1, x1, exact=False)
            
            for x2 in range(lower_limit_x2, a2 * x1 + 1):
                c_a2x1_x2 = comb(a2 * x1, x2, exact=False)
                c_a3x2_x3 = comb(a3 * x2, x3, exact=False)
                term_x2_base = c_a2x1_x2 * c_a3x2_x3
                
                for j1 in range(0, a1 - x1 + 1):
                    c_j1 = comb(a1 - x1, j1, exact=False) * (-1)**j1
                    
                    for j2 in range(0, a2 * x1 - x2 + 1):
                        c_j2 = comb(a2 * x1 - x2, j2, exact=False) * (-1)**j2
                        
                        for j3 in range(0, a3 * x2 - x3 + 1):
                            c_j3 = comb(a3 * x2 - x3, j3, exact=False) * (-1)**j3
                            
                            # Calculate the constant factors in the exponents for the integral
                            A = l0 + l1 * (x1 + j1) + l2 * (x2 + j2)
                            B = l3 * (x3 + j3)
                            
                            # Define the integrand
                            # e^(-A*t) * e^(-B*t^b3)
                            integrand = lambda t: np.exp(-A * t - B * t**b3)
                            
                            # Compute the integral from 0 to infinity
                            # quad returns (integral_value, absolute_error_estimate)
                            integral_val, _ = integrate.quad(integrand, 0, np.inf)
                            
                            # Accumulate
                            total_sum += (c_a1_x1 * term_x2_base * c_j1 * c_j2 * c_j3 * integral_val)
                            
        # Numerical integration of alternating sums can introduce floating-point
        # artifacts; mean time cannot be negative in a physical reliability model.
        return max(total_sum, 0.0)


    def get_T3W_sympy():
        """
        Symbolic implementation using sympy for display and algebraic manipulation.
        """
        x3, t = sp.symbols('x_3 t', real=True, positive=True)
        l0, l1, l2, l3 = sp.symbols('lambda_0 lambda_1 lambda_2 lambda_3', real=True, positive=True)
        a1, a2, a3 = sp.symbols('a_1 a_2 a_3', integer=True, positive=True)
        b3 = sp.symbols('beta_3', real=True, positive=True)
        x1, x2, j1, j2, j3 = sp.symbols('x_1 x_2 j_1 j_2 j_3', integer=True)

        # Limits
        lower_limit_x2 = sp.ceiling(x3 / a3)
        lower_limit_x1 = sp.ceiling(lower_limit_x2 / a2)

        # The integrand and Integral
        exponent_part1 = (l0 + l1*(x1 + j1) + l2*(x2 + j2)) * t
        exponent_part2 = l3 * (x3 + j3) * t**b3
        integrand = sp.exp(-exponent_part1) * sp.exp(-exponent_part2)
        
        # sp.oo represents infinity in sympy
        integral_term = sp.Integral(integrand, (t, 0, sp.oo))

        # Sum over j3
        term_j3 = sp.binomial(a3 * x2 - x3, j3) * (-1)**j3 * integral_term
        sum_j3 = sp.Sum(term_j3, (j3, 0, a3 * x2 - x3))

        # Sum over j2
        term_j2 = sp.binomial(a2 * x1 - x2, j2) * (-1)**j2 * sum_j3
        sum_j2 = sp.Sum(term_j2, (j2, 0, a2 * x1 - x2))

        # Sum over j1
        term_j1 = sp.binomial(a1 - x1, j1) * (-1)**j1 * sum_j2
        sum_j1 = sp.Sum(term_j1, (j1, 0, a1 - x1))

        # Sum over x2
        term_x2 = sp.binomial(a2 * x1, x2) * sp.binomial(a3 * x2, x3) * sum_j1
        sum_x2 = sp.Sum(term_x2, (x2, lower_limit_x2, a2 * x1))

        # Sum over x1 (Outermost)
        term_x1 = sp.binomial(a1, x1) * sum_x2
        T_3W = sp.Sum(term_x1, (x1, lower_limit_x1, a1))

        return T_3W

    return compute_T3W_numpy, get_T3W_sympy


def get_T_Gamma_3W_sympy():
    """
    Symbolic formula for T_Γ3W(k): mean time to failure with redundancy.
    T_Gamma_3W(k) = Sum(T_3W(x_3), (x_3, k, a_1 * a_2 * a_3))
    Returns a SymPy Eq for display/LaTeX.
    """
    k, x_3, a_1, a_2, a_3 = sp.symbols("k x_3 a_1 a_2 a_3", integer=True, nonnegative=True)
    T_Gamma_3W = sp.Function("T_{\\Gamma 3W}")
    T_3W = sp.Function("T_{3W}")
    right_side = sp.Sum(T_3W(x_3), (x_3, k, a_1 * a_2 * a_3))
    return sp.Eq(T_Gamma_3W(k), right_side)