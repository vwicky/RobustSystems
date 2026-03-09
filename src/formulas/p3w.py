import sympy as sp
import numpy as np
from scipy.special import comb

def get_P3W_functions():
    """
    Returns two functions for evaluating and displaying the P_3W formula.
    
    Returns:
        tuple: (compute_P3W_numpy, get_P3W_sympy)
    """
    
    def compute_P3W_numpy(x3, t, l0, l1, l2, l3, a1, a2, a3, b3):
        """
        Numerical implementation using numpy and scipy for computation.
        't' can be a scalar or a numpy array.
        """
        # Ensure t is a numpy array for vectorized operations if a list/scalar is passed
        t = np.asarray(t)
        
        # Calculate lower limits using ceiling
        lower_limit_x2 = int(np.ceil(x3 / a3))
        lower_limit_x1 = int(np.ceil(lower_limit_x2 / a2))
        
        outer_sum = np.zeros_like(t, dtype=float)
        
        # Outer summation over x1
        for x1 in range(lower_limit_x1, a1 + 1):
            
            inner_sum = np.zeros_like(t, dtype=float)
            
            # Inner summation over x2
            for x2 in range(lower_limit_x2, a2 * x1 + 1):
                # Calculate the parts of the inner term
                c_a2x1_x2 = comb(a2 * x1, x2, exact=False)
                c_a3x2_x3 = comb(a3 * x2, x3, exact=False)
                
                part2 = c_a2x1_x2 * np.exp(-l2 * x2 * t) * (1 - np.exp(-l2 * t))**(a2 * x1 - x2)
                part3 = c_a3x2_x3 * np.exp(-l3 * x3 * t**b3) * (1 - np.exp(-l3 * t**b3))**(a3 * x2 - x3)
                
                inner_sum += part2 * part3
            
            # Calculate the parts of the outer term
            c_a1_x1 = comb(a1, x1, exact=False)
            part1 = c_a1_x1 * np.exp(-l1 * x1 * t) * (1 - np.exp(-l1 * t))**(a1 - x1)
            
            outer_sum += part1 * inner_sum
            
        # Final multiplication by the leading exponential term
        return np.exp(-l0 * t) * outer_sum


    def get_P3W_sympy():
        """
        Symbolic implementation using sympy for display and algebraic manipulation.
        """
        x3, t = sp.symbols('x_3 t', real=True, positive=True)
        l0, l1, l2, l3 = sp.symbols('lambda_0 lambda_1 lambda_2 lambda_3', real=True, positive=True)
        a1, a2, a3 = sp.symbols('a_1 a_2 a_3', integer=True, positive=True)
        b3 = sp.symbols('beta_3', real=True, positive=True)
        x1, x2 = sp.symbols('x_1 x_2', integer=True)

        # Limits
        lower_limit_x2 = sp.ceiling(x3 / a3)
        lower_limit_x1 = sp.ceiling(lower_limit_x2 / a2)

        # Inner expression
        inner_term = (
            sp.binomial(a2 * x1, x2) 
            * sp.exp(-l2 * x2 * t) * (1 - sp.exp(-l2 * t))**(a2 * x1 - x2) 
            * sp.binomial(a3 * x2, x3) 
            * sp.exp(-l3 * x3 * t**b3) * (1 - sp.exp(-l3 * t**b3))**(a3 * x2 - x3)
        )
        inner_sum = sp.Sum(inner_term, (x2, lower_limit_x2, a2 * x1))

        # Outer expression
        outer_term = (
            sp.binomial(a1, x1) 
            * sp.exp(-l1 * x1 * t) * (1 - sp.exp(-l1 * t))**(a1 - x1) 
            * inner_sum
        )
        outer_sum = sp.Sum(outer_term, (x1, lower_limit_x1, a1))

        # Full equation
        P_3W = sp.exp(-l0 * t) * outer_sum

        return P_3W

    return compute_P3W_numpy, get_P3W_sympy