import sympy as sp
import numpy as np
from scipy.special import comb

def get_a3W_functions():
    """
    Returns two functions for evaluating and displaying the a_3W formula.
    
    Returns:
        tuple: (compute_a3W_numpy, get_a3W_sympy)
    """
    
    def compute_a3W_numpy(k, t, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerical implementation using nested loops.
        't' can be a scalar or a numpy array for vectorized time series calculation.
        """
        # Ensure t is a numpy array
        t = np.asarray(t, dtype=float)
        total_sum = np.zeros_like(t, dtype=float)
        
        # Outermost loop over x3
        for x3 in range(k, a1 * a2 * a3 + 1):
            
            lower_limit_x2 = int(np.ceil(x3 / a3))
            lower_limit_x1 = int(np.ceil(lower_limit_x2 / a2))
            
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
                                
                                # Pre-calculate repeated variables for clarity and speed
                                A = l1 * (x1 + j1) + l2 * (x2 + j2)
                                B = l3 * (x3 + j3)
                                
                                # The complex inner expression evaluated at t
                                multiplier = (B * b3 * t**(b3 - 1) + l0 + A)
                                inner_expr = multiplier * np.exp(-A * t) * np.exp(-B * t**b3)
                                
                                # Accumulate into the grand total
                                total_sum += (c_a1_x1 * term_x2_base * c_j1 * c_j2 * c_j3 * inner_expr)
                            
        # Multiply by the leading exponential term
        return np.exp(-l0 * t) * total_sum


    def get_a3W_sympy():
        """
        Symbolic implementation using sympy for display and algebraic manipulation.
        """
        k, t = sp.symbols('k t', real=True, positive=True)
        l0, l1, l2, l3 = sp.symbols('lambda_0 lambda_1 lambda_2 lambda_3', real=True, positive=True)
        a1, a2, a3 = sp.symbols('a_1 a_2 a_3', integer=True, positive=True)
        b3 = sp.symbols('beta_3', real=True, positive=True)
        x1, x2, x3, j1, j2, j3 = sp.symbols('x_1 x_2 x_3 j_1 j_2 j_3', integer=True)

        # Limits for inner sums
        lower_limit_x2 = sp.ceiling(x3 / a3)
        lower_limit_x1 = sp.ceiling(lower_limit_x2 / a2)

        # Constructing the inner expression
        A = l1 * (x1 + j1) + l2 * (x2 + j2)
        B = l3 * (x3 + j3)
        multiplier = B * b3 * t**(b3 - 1) + l0 + A
        inner_expr = multiplier * sp.exp(-A * t) * sp.exp(-B * t**b3)

        # Sum over j3
        term_j3 = sp.binomial(a3 * x2 - x3, j3) * (-1)**j3 * inner_expr
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

        # Sum over x1
        term_x1 = sp.binomial(a1, x1) * sum_x2
        sum_x1 = sp.Sum(term_x1, (x1, lower_limit_x1, a1))

        # Sum over x3 (Outermost)
        total_sum = sp.Sum(sum_x1, (x3, k, a1 * a2 * a3))
        
        # Apply the leading exponential
        a_3W = sp.exp(-l0 * t) * total_sum

        return a_3W

    return compute_a3W_numpy, get_a3W_sympy