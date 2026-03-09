import sympy as sp
import numpy as np
from scipy.special import comb

def get_K_G3W_functions():
    """
    Returns two functions for evaluating and displaying the K_Gamma_3W formula.
    
    Returns:
        tuple: (compute_K_G3W_numpy, get_K_G3W_sympy)
    """
    
    def compute_K_G3W_numpy(k, t, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerical implementation using numpy and scipy for computation.
        't' can be a scalar or a numpy array.
        """
        # Ensure t is a numpy array for vectorized operations
        t = np.asarray(t)
        
        total_sum_x3 = np.zeros_like(t, dtype=float)
        
        # New Outermost summation over x3
        for x3 in range(k, a1 * a2 * a3 + 1):
            
            # Calculate lower limits for inner sums based on current x3
            lower_limit_x2 = int(np.ceil(x3 / a3))
            lower_limit_x1 = int(np.ceil(lower_limit_x2 / a2))
            
            outer_sum_x1 = np.zeros_like(t, dtype=float)
            
            # Middle summation over x1
            for x1 in range(lower_limit_x1, a1 + 1):
                
                inner_sum_x2 = np.zeros_like(t, dtype=float)
                
                # Innermost summation over x2
                for x2 in range(lower_limit_x2, a2 * x1 + 1):
                    c_a2x1_x2 = comb(a2 * x1, x2, exact=False)
                    c_a3x2_x3 = comb(a3 * x2, x3, exact=False)
                    
                    part2 = c_a2x1_x2 * np.exp(-l2 * x2 * t) * (1 - np.exp(-l2 * t))**(a2 * x1 - x2)
                    part3 = c_a3x2_x3 * np.exp(-l3 * x3 * t**b3) * (1 - np.exp(-l3 * t**b3))**(a3 * x2 - x3)
                    
                    inner_sum_x2 += part2 * part3
                
                c_a1_x1 = comb(a1, x1, exact=False)
                part1 = c_a1_x1 * np.exp(-l1 * x1 * t) * (1 - np.exp(-l1 * t))**(a1 - x1)
                
                outer_sum_x1 += part1 * inner_sum_x2
                
            total_sum_x3 += outer_sum_x1
            
        # Final multiplication by the leading exponential term
        return np.exp(-l0 * t) * total_sum_x3


    def get_K_G3W_sympy():
        """
        Symbolic implementation using sympy for display and algebraic manipulation.
        """
        k, t = sp.symbols('k t', real=True, positive=True)
        l0, l1, l2, l3 = sp.symbols('lambda_0 lambda_1 lambda_2 lambda_3', real=True, positive=True)
        a1, a2, a3 = sp.symbols('a_1 a_2 a_3', integer=True, positive=True)
        b3 = sp.symbols('beta_3', real=True, positive=True)
        x1, x2, x3 = sp.symbols('x_1 x_2 x_3', integer=True)

        # Limits for inner sums
        lower_limit_x2 = sp.ceiling(x3 / a3)
        lower_limit_x1 = sp.ceiling(lower_limit_x2 / a2)

        # Innermost expression
        inner_term = (
            sp.binomial(a2 * x1, x2) 
            * sp.exp(-l2 * x2 * t) * (1 - sp.exp(-l2 * t))**(a2 * x1 - x2) 
            * sp.binomial(a3 * x2, x3) 
            * sp.exp(-l3 * x3 * t**b3) * (1 - sp.exp(-l3 * t**b3))**(a3 * x2 - x3)
        )
        sum_x2 = sp.Sum(inner_term, (x2, lower_limit_x2, a2 * x1))

        # Middle expression
        middle_term = (
            sp.binomial(a1, x1) 
            * sp.exp(-l1 * x1 * t) * (1 - sp.exp(-l1 * t))**(a1 - x1) 
            * sum_x2
        )
        sum_x1 = sp.Sum(middle_term, (x1, lower_limit_x1, a1))

        # Outermost expression
        sum_x3 = sp.Sum(sum_x1, (x3, k, a1 * a2 * a3))

        # Full equation
        K_G3W = sp.exp(-l0 * t) * sum_x3

        return K_G3W

    return compute_K_G3W_numpy, get_K_G3W_sympy