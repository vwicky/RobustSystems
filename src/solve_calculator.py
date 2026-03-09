import sympy  # <-- REQUIRED IMPORT ADDED
from src.input_dataclass import InputData
import time
from typing import Any
import math
from tqdm import tqdm

from src.formulas.p3w import get_P3W_functions
from src.formulas.kh3w import get_K_G3W_functions
from src.formulas.t3w import get_T3W_functions
from src.formulas.a3w import get_a3W_functions

from src.cache import Cache

"""
    NOTE:
    The probability of failure-free operation for the 3rd-level elements follows 
    a Weibull distribution, while the elements of other levels follow 
    an exponential distribution.
"""

class SolverCalculator:
    def __init__(self, input_data: InputData):
        self.input_data = input_data
        self.cache = Cache(var_id=self.input_data.var_id)
    
    def check_time(self, function) -> tuple[tuple[Any, str] | None, float, Exception | None]:
        start_time = time.time()
        error: Exception | None = None

        try:
            result = function()
        except Exception as e:
            result = None
            error = e

        end_time = time.time()
        elapsed_time = end_time - start_time

        return result, elapsed_time, error
    
    def check_in_cache(self, formula: str, *args, **kwargs) -> Any:
        return self.cache.find(key=formula)

    def find_P_3W(self, use_cache: bool = True) -> tuple[list, str]:
        """ 
            Computes a list of P_3W(x3, t3) for x3 in [0, a1 * a2 * a3]
        """
        cached_result = self.check_in_cache("P_3W")
        if cached_result and use_cache:
            return cached_result

        p = self.input_data
        compute_func, visual_func = get_P3W_functions()

        results = []
        max_x3 = p.a1 * p.a2 * p.a3
        
        for x3 in range(0, max_x3 + 1):
            result = compute_func(
                x3=x3,
                t=p.t,
                l0=p.lambda0,
                l1=p.lambda1,
                l2=p.lambda2,
                l3=p.lambda3,
                a1=p.a1,
                a2=p.a2,
                a3=p.a3,
                b3=p.beta,
            )
            results.append(float(result))

        # FIXED: Convert to LaTeX once, cache it, AND return it
        latex_str = sympy.latex(visual_func())
        self.cache.add("P_3W", (results, latex_str))
        return results, latex_str
    
    def find_K_Г3W(self, use_cache: bool = True) -> tuple[float, str]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("K_Г3W")
        if cached_result and use_cache:
            return cached_result
        
        p = self.input_data
        compute_func, visual_func = get_K_G3W_functions()

        result = compute_func(
            k=p.k,
            t=p.t,
            l0=p.lambda0,
            l1=p.lambda1,
            l2=p.lambda2,
            l3=p.lambda3,
            a1=p.a1,
            a2=p.a2,
            a3=p.a3,
            b3=p.beta,
        )

        latex_str = sympy.latex(visual_func())
        self.cache.add("K_Г3W", (float(result), latex_str))
        return float(result), latex_str
    
    def find_1_minus_K_Г3W(self, use_cache: bool = True) -> tuple[float, str]:
        """
        Return value itself and step by step human-readable explanations, simpy plots, etc
        """
        # FIXED: Cleaned up the old 'False' argument and double-cache check
        cached_result = self.check_in_cache("1_minus_K_Г3W")
        if cached_result and use_cache:
            return cached_result

        k_h3w, _ = self.find_K_Г3W()
        result = 1 - k_h3w

        self.cache.add("1_minus_K_Г3W", (result, "1 - K_{\\Gamma 3W}"))
        return result, "1 - K_{\\Gamma 3W}"
    
    def find_T_3W(self, use_cache: bool = True) -> tuple[list[float], str]:
        """ 
        Computes a list of T_3W(x3, t3) for x3 in [0, a1 * a2 * a3]
        """
        cached_result = self.check_in_cache("T_3W")
        if cached_result and use_cache:
            cached_values, cached_latex = cached_result
            if isinstance(cached_values, list) and all(
                isinstance(v, (int, float)) and math.isfinite(v) for v in cached_values
            ):
                sanitized_values = [max(float(v), 0.0) for v in cached_values]
                if sanitized_values != cached_values:
                    self.cache.add("T_3W", (sanitized_values, cached_latex))
                return sanitized_values, cached_latex

        p = self.input_data
        compute_func, visual_func = get_T3W_functions()

        results = []
        max_x3 = p.a1 * p.a2 * p.a3
        
        for x3 in tqdm(range(max_x3 + 1), desc="Computing T_3W", unit="x3"):
            result = compute_func(
                x3=x3,
                l0=p.lambda0,
                l1=p.lambda1,
                l2=p.lambda2,
                l3=p.lambda3,
                a1=p.a1,
                a2=p.a2,
                a3=p.a3,
                b3=p.beta,
            )
            results.append(float(result))

        latex_str = sympy.latex(visual_func())
        self.cache.add("T_3W", (results, latex_str))
        return results, latex_str
    
    def find_T_Г3W(self, use_cache: bool = True) -> tuple[float, str]:
        """ 
        NOTE: Requires heavy recompute of T_3W - cache implemented
        """
        cached_result = self.check_in_cache("T_Г3W")
        if cached_result and use_cache:
            cached_value, cached_latex = cached_result
            if (
                isinstance(cached_value, (int, float))
                and math.isfinite(cached_value)
                and 0 <= cached_value <= 1e18
            ):
                return cached_result
        
        p = self.input_data

        t3w_data = self.check_in_cache("T_3W")
        if t3w_data:
            t3w, _ = t3w_data
        else:
            t3w, _ = self.find_T_3W()

        valid_terms = []
        for i in range(p.k, p.a1 * p.a2 * p.a3 + 1):
            value = float(t3w[i])
            if not math.isfinite(value):
                continue
            # Physical safeguard: MTTF contributions cannot be negative.
            valid_terms.append(max(value, 0.0))

        if not valid_terms:
            raise ValueError("T_Г3W cannot be computed: no finite non-negative T_3W terms.")

        result_sum = math.fsum(valid_terms)
        if result_sum > 1e18:
            raise ValueError(
                "T_Г3W is numerically unstable (unrealistically large). "
                "Try reducing parameter ranges or using a smaller model."
            )

        self.cache.add("T_Г3W", (result_sum, "T_{\\Gamma 3W}"))
        return result_sum, "T_{\\Gamma 3W}"
    
    def find_Q_3W(self, use_cache: bool = True) -> tuple[float, str]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("Q_3W")
        if cached_result and use_cache:
            return cached_result
        
        k_h3w, _ = self.find_K_Г3W()
        result = 1 - k_h3w

        self.cache.add("Q_3W", (result, "1 - K_{\\Gamma 3W}"))
        return result, "1 - K_{\\Gamma 3W}"
    
    def find_a_3W(self, use_cache: bool = True) -> tuple[float, str]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("a_3W")
        if cached_result and use_cache:
            return cached_result
        
        p = self.input_data
        compute_func, visual_func = get_a3W_functions()

        result = compute_func(
            k=p.k,
            t=p.t,
            l0=p.lambda0,
            l1=p.lambda1,
            l2=p.lambda2,
            l3=p.lambda3,
            a1=p.a1,
            a2=p.a2,
            a3=p.a3,
            b3=p.beta,
        )

        latex_str = sympy.latex(visual_func())
        self.cache.add("a_3W", (float(result), latex_str))
        return float(result), latex_str
    
    def find_lambda_3W(self, use_cache: bool = True) -> tuple[float, str]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("lambda_3W")
        if cached_result and use_cache:
            return cached_result

        a3w, _ = self.find_a_3W()
        k_h3w, _ = self.find_K_Г3W()

        if abs(k_h3w) < 1e-12:
            raise ZeroDivisionError(
                "K_Г3W is too close to zero; lambda_3W cannot be computed safely."
            )

        result = a3w / k_h3w

        self.cache.add("lambda_3W", (result, "\\frac{a_{3W}}{K_{\\Gamma 3W}}"))
        return result, "\\frac{a_{3W}}{K_{\\Gamma 3W}}"

    def clear_cache(self) -> bool:
        return self.cache.clear()