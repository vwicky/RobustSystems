import sympy  # <-- REQUIRED IMPORT ADDED
from src.input_dataclass import InputData
import time
from typing import Any
import math
from tqdm import tqdm
from scipy.special import comb
from scipy import integrate

from src.formulas.p3w import get_P3W_functions
from src.formulas.kh3w import get_K_G3W_functions
from src.formulas.t3w import get_T3W_functions, get_T_Gamma_3W_sympy
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

    @staticmethod
    def _fmt_number(value: float) -> str:
        return f"{value:.6g}"

    def _sample_x_points(self, n_max: int) -> list[int]:
        candidates = [0, 1, 2, 3, n_max // 2, n_max]
        unique = []
        for c in candidates:
            if 0 <= c <= n_max and c not in unique:
                unique.append(c)
        return unique

    def _p3w_seed_term(self, x3: int) -> dict[str, float | int]:
        p = self.input_data
        lower_x2 = int(math.ceil(x3 / p.a3))
        lower_x1 = int(math.ceil(lower_x2 / p.a2))
        x1 = max(lower_x1, 0)
        x2 = max(lower_x2, 0)

        c_a1_x1 = float(comb(p.a1, x1, exact=False))
        c_a2x1_x2 = float(comb(p.a2 * x1, x2, exact=False))
        c_a3x2_x3 = float(comb(p.a3 * x2, x3, exact=False))

        part1 = c_a1_x1 * math.exp(-p.lambda1 * x1 * p.t) * (1 - math.exp(-p.lambda1 * p.t)) ** (p.a1 - x1)
        part2 = c_a2x1_x2 * math.exp(-p.lambda2 * x2 * p.t) * (1 - math.exp(-p.lambda2 * p.t)) ** (p.a2 * x1 - x2)
        part3 = c_a3x2_x3 * math.exp(-p.lambda3 * x3 * (p.t ** p.beta)) * (
            1 - math.exp(-p.lambda3 * (p.t ** p.beta))
        ) ** (p.a3 * x2 - x3)
        lead = math.exp(-p.lambda0 * p.t)
        seed = lead * part1 * part2 * part3

        return {
            "x1_min": x1,
            "x2_min": x2,
            "c1": c_a1_x1,
            "c2": c_a2x1_x2,
            "c3": c_a3x2_x3,
            "lead": lead,
            "part1": part1,
            "part2": part2,
            "part3": part3,
            "seed": seed,
        }

    def _t3w_seed_term(self, x3: int) -> dict[str, float | int]:
        p = self.input_data
        lower_x2 = int(math.ceil(x3 / p.a3))
        lower_x1 = int(math.ceil(lower_x2 / p.a2))
        x1 = max(lower_x1, 0)
        x2 = max(lower_x2, 0)
        j1 = j2 = j3 = 0

        coef = float(comb(p.a1, x1, exact=False)) * float(comb(p.a2 * x1, x2, exact=False)) * float(
            comb(p.a3 * x2, x3, exact=False)
        )
        A = p.lambda0 + p.lambda1 * (x1 + j1) + p.lambda2 * (x2 + j2)
        B = p.lambda3 * (x3 + j3)
        integral_val, _ = integrate.quad(lambda tt: math.exp(-A * tt - B * (tt ** p.beta)), 0, math.inf)
        seed = coef * integral_val

        return {
            "x1_min": x1,
            "x2_min": x2,
            "coef": coef,
            "A": A,
            "B": B,
            "integral": integral_val,
            "seed": seed,
        }

    def _a3w_seed_term(self, x3: int) -> dict[str, float | int]:
        p = self.input_data
        lower_x2 = int(math.ceil(x3 / p.a3))
        lower_x1 = int(math.ceil(lower_x2 / p.a2))
        x1 = max(lower_x1, 0)
        x2 = max(lower_x2, 0)
        j1 = j2 = j3 = 0

        coef = float(comb(p.a1, x1, exact=False)) * float(comb(p.a2 * x1, x2, exact=False)) * float(
            comb(p.a3 * x2, x3, exact=False)
        )
        A = p.lambda1 * (x1 + j1) + p.lambda2 * (x2 + j2)
        B = p.lambda3 * (x3 + j3)
        multiplier = B * p.beta * (p.t ** (p.beta - 1)) + p.lambda0 + A
        inner = multiplier * math.exp(-A * p.t) * math.exp(-B * (p.t ** p.beta))
        lead = math.exp(-p.lambda0 * p.t)
        seed = lead * coef * inner

        return {
            "x1_min": x1,
            "x2_min": x2,
            "coef": coef,
            "A": A,
            "B": B,
            "multiplier": multiplier,
            "inner": inner,
            "lead": lead,
            "seed": seed,
        }

    def _with_steps(self, cached_result: Any, steps_builder) -> tuple[Any, str, list[str]]:
        if (
            isinstance(cached_result, (list, tuple))
            and len(cached_result) == 3
        ):
            value, latex, steps = cached_result
            if not steps or len(steps) < 5:
                steps = steps_builder(value)
            return value, latex, steps or []
        if (
            isinstance(cached_result, (list, tuple))
            and len(cached_result) == 2
        ):
            value, latex = cached_result
            steps = steps_builder(value)
            return value, latex, steps
        return None, "", []

    def find_P_3W(self, use_cache: bool = True) -> tuple[list, str, list[str]]:
        """ 
            Computes a list of P_3W(x3, t3) for x3 in [0, a1 * a2 * a3]
        """
        cached_result = self.check_in_cache("P_3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_p3w)

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
        steps = self._steps_for_p3w(results)
        self.cache.add("P_3W", (results, latex_str, steps))
        return results, latex_str, steps
    
    def find_K_Г3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("K_Г3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_k_gamma)
        
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
        numeric = float(result)
        steps = self._steps_for_k_gamma(numeric)
        self.cache.add("K_Г3W", (numeric, latex_str, steps))
        return numeric, latex_str, steps
    
    def find_1_minus_K_Г3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """
        Return value itself and step by step human-readable explanations, simpy plots, etc
        """
        # FIXED: Cleaned up the old 'False' argument and double-cache check
        cached_result = self.check_in_cache("1_minus_K_Г3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_q3w)

        k_h3w, _, _ = self.find_K_Г3W()
        result = 1 - k_h3w

        steps = self._steps_for_q3w(result)
        self.cache.add("1_minus_K_Г3W", (result, "1 - K_{\\Gamma 3W}", steps))
        return result, "1 - K_{\\Gamma 3W}", steps
    
    def find_T_3W(self, use_cache: bool = True) -> tuple[list[float], str, list[str]]:
        """ 
        Computes a list of T_3W(x3, t3) for x3 in [0, a1 * a2 * a3]
        """
        cached_result = self.check_in_cache("T_3W")
        if cached_result and use_cache:
            cached_values, cached_latex, cached_steps = self._with_steps(cached_result, self._steps_for_t3w)
            if isinstance(cached_values, list) and all(
                isinstance(v, (int, float)) and math.isfinite(v) for v in cached_values
            ):
                sanitized_values = [max(float(v), 0.0) for v in cached_values]
                if sanitized_values != cached_values:
                    self.cache.add("T_3W", (sanitized_values, cached_latex, cached_steps))
                return sanitized_values, cached_latex, cached_steps

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
        steps = self._steps_for_t3w(results)
        self.cache.add("T_3W", (results, latex_str, steps))
        return results, latex_str, steps
    
    def find_T_Г3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """ 
        NOTE: Requires heavy recompute of T_3W - cache implemented
        """
        cached_result = self.check_in_cache("T_Г3W")
        if cached_result and use_cache:
            cached_value, cached_latex, cached_steps = self._with_steps(cached_result, self._steps_for_t_gamma)
            if (
                isinstance(cached_value, (int, float))
                and math.isfinite(cached_value)
                and 0 <= cached_value <= 1e18
            ):
                return cached_value, cached_latex, cached_steps
        
        p = self.input_data

        t3w_data = self.check_in_cache("T_3W")
        if t3w_data:
            t3w, _, _ = self._with_steps(t3w_data, self._steps_for_t3w)
        else:
            t3w, _, _ = self.find_T_3W()

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

        steps = self._steps_for_t_gamma(result_sum, valid_terms)
        latex_str = sympy.latex(get_T_Gamma_3W_sympy())
        self.cache.add("T_Г3W", (result_sum, latex_str, steps))
        return result_sum, latex_str, steps
    
    def find_Q_3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("Q_3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_q3w)
        
        k_h3w, _, _ = self.find_K_Г3W()
        result = 1 - k_h3w

        steps = self._steps_for_q3w(result)
        self.cache.add("Q_3W", (result, "1 - K_{\\Gamma 3W}", steps))
        return result, "1 - K_{\\Gamma 3W}", steps
    
    def find_a_3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("a_3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_a3w)
        
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
        numeric = float(result)
        steps = self._steps_for_a3w(numeric)
        self.cache.add("a_3W", (numeric, latex_str, steps))
        return numeric, latex_str, steps
    
    def find_lambda_3W(self, use_cache: bool = True) -> tuple[float, str, list[str]]:
        """ 
        Return value itself and step by step human-readable explanations, simpy plots, etc 
        """
        cached_result = self.check_in_cache("lambda_3W")
        if cached_result and use_cache:
            return self._with_steps(cached_result, self._steps_for_lambda3w)

        a3w, _, _ = self.find_a_3W()
        k_h3w, _, _ = self.find_K_Г3W()

        if abs(k_h3w) < 1e-12:
            raise ZeroDivisionError(
                "K_Г3W is too close to zero; lambda_3W cannot be computed safely."
            )

        result = a3w / k_h3w

        steps = self._steps_for_lambda3w(result)
        self.cache.add("lambda_3W", (result, "\\frac{a_{3W}}{K_{\\Gamma 3W}}", steps))
        return result, "\\frac{a_{3W}}{K_{\\Gamma 3W}}", steps

    def _steps_for_p3w(self, values: list[float]) -> list[str]:
        p = self.input_data
        max_x3 = p.a1 * p.a2 * p.a3
        samples = []
        for x in self._sample_x_points(max_x3):
            seed = self._p3w_seed_term(x)
            samples.append(
                f"x3={x}: x2_min=ceil({x}/{p.a3})={seed['x2_min']}, "
                f"x1_min=ceil({seed['x2_min']}/{p.a2})={seed['x1_min']}, "
                f"C1={self._fmt_number(float(seed['c1']))}, C2={self._fmt_number(float(seed['c2']))}, C3={self._fmt_number(float(seed['c3']))}, "
                f"seed=exp(-lambda0*t)*part1*part2*part3={self._fmt_number(float(seed['seed']))}, "
                f"full_sum P_3W({x})={self._fmt_number(values[x])}"
            )
        last_value = self._fmt_number(values[-1]) if values else "n/a"
        min_value = self._fmt_number(min(values)) if values else "n/a"
        max_value = self._fmt_number(max(values)) if values else "n/a"
        steps = [
            f"1) Задано параметри: t={self._fmt_number(p.t)}, a1={p.a1}, a2={p.a2}, a3={p.a3}, beta={self._fmt_number(p.beta)}.",
            f"2) Проміжний крок: N=a1*a2*a3={p.a1}*{p.a2}*{p.a3}={max_x3}.",
            f"3) Обчислення виконується для кожного x3: 0..{max_x3} (усього {len(values)} точок).",
            "4) Для кожного x3 спочатку рахується seed-внесок (мінімальні x1,x2), а потім повна подвійна сума по x1,x2.",
            "5) Деталізація обчислення для вибраних x3:",
        ]
        for sample in samples:
            steps.append(f"   - {sample}")
        steps.extend(
            [
                f"6) Перевірка діапазону: min(P_3W)={min_value}, max(P_3W)={max_value}.",
                f"7) Кінцева точка масиву: P_3W(x3={max_x3})={last_value}.",
            ]
        )
        return steps

    def _steps_for_k_gamma(self, result: float) -> list[str]:
        p = self.input_data
        n_total = p.a1 * p.a2 * p.a3
        r0 = math.exp(-p.lambda0 * p.t)
        r1 = math.exp(-p.lambda1 * p.t)
        r2 = math.exp(-p.lambda2 * p.t)
        r3 = math.exp(-((p.lambda3 * p.t) ** p.beta))
        return [
            f"1) Підставлено в K_Г3W(k,t): k={p.k}, t={self._fmt_number(p.t)}.",
            f"2) Проміжний крок: N=a1*a2*a3={p.a1}*{p.a2}*{p.a3}={n_total}, поріг готовності k={p.k}.",
            f"3) Проміжні надійності рівнів у момент t: R0=exp(-lambda0*t)={self._fmt_number(r0)}, R1={self._fmt_number(r1)}, R2={self._fmt_number(r2)}, R3_Weibull={self._fmt_number(r3)}.",
            f"4) Після підстановки всіх параметрів у формулу отримано K_Г3W={self._fmt_number(result)}.",
        ]

    def _steps_for_q3w(self, result: float) -> list[str]:
        k_h3w, _, _ = self.find_K_Г3W()
        one_val = 1.0
        delta = one_val - k_h3w
        return [
            "1) Використано формулу Q_3W = 1 - K_Г3W.",
            f"2) Проміжний крок: K_Г3W={self._fmt_number(k_h3w)}.",
            f"3) Арифметика: 1 - K_Г3W = {self._fmt_number(one_val)} - {self._fmt_number(k_h3w)} = {self._fmt_number(delta)}.",
            f"4) Підсумок: Q_3W={self._fmt_number(result)}.",
        ]

    def _steps_for_t3w(self, values: list[float]) -> list[str]:
        p = self.input_data
        max_x3 = p.a1 * p.a2 * p.a3
        samples = []
        for x in self._sample_x_points(max_x3):
            seed = self._t3w_seed_term(x)
            samples.append(
                f"x3={x}: x2_min={seed['x2_min']}, x1_min={seed['x1_min']}, "
                f"A=lambda0+lambda1*x1+lambda2*x2={self._fmt_number(float(seed['A']))}, "
                f"B=lambda3*x3={self._fmt_number(float(seed['B']))}, "
                f"I0=int(exp(-A*t-B*t^beta),0..inf)={self._fmt_number(float(seed['integral']))}, "
                f"coef=C(a1,x1)C(a2*x1,x2)C(a3*x2,x3)={self._fmt_number(float(seed['coef']))}, "
                f"seed=coef*I0={self._fmt_number(float(seed['seed']))}, "
                f"full_sum T_3W({x})={self._fmt_number(values[x])}"
            )
        min_value = self._fmt_number(min(values)) if values else "n/a"
        max_value = self._fmt_number(max(values)) if values else "n/a"
        steps = [
            f"1) Обчислюється T_3W(x3) для x3=0..{max_x3}.",
            f"2) Проміжний крок: N=a1*a2*a3={p.a1}*{p.a2}*{p.a3}={max_x3}.",
            f"3) Обчислено {len(values)} проміжних значень T_3W(x3).",
            "4) Для кожного x3 рахується багатовимірна сума; нижче показано конкретні seed-обчислення (j1=j2=j3=0) і повний результат.",
            "5) Деталізація для вибраних x3:",
        ]
        for sample in samples:
            steps.append(f"   - {sample}")
        steps.append(f"6) Перевірка діапазону: min(T_3W)={min_value}, max(T_3W)={max_value}.")
        return steps

    def _steps_for_t_gamma(self, result: float, valid_terms: list[float] | None = None) -> list[str]:
        p = self.input_data
        terms = valid_terms
        if terms is None:
            t3w, _, _ = self.find_T_3W()
            terms = [max(float(t3w[i]), 0.0) for i in range(p.k, p.a1 * p.a2 * p.a3 + 1)]
        preview_terms = []
        for idx, value in enumerate(terms[:5], start=p.k):
            preview_terms.append(f"T_3W({idx})={self._fmt_number(value)}")
        partial_sum = math.fsum(terms[:5]) if terms else 0.0
        return [
            f"1) Використано суму T_Г3W = Σ T_3W(i) для i від k={p.k} до N={p.a1 * p.a2 * p.a3}.",
            f"2) Кількість доданків у сумі: N-k+1={p.a1 * p.a2 * p.a3}-{p.k}+1={len(terms)}.",
            "3) Перші доданки суми: " + "; ".join(preview_terms) + ".",
            f"4) Проміжна часткова сума перших 5 доданків: {self._fmt_number(partial_sum)}.",
            f"5) Повна сума: T_Г3W={self._fmt_number(result)}.",
        ]

    def _steps_for_a3w(self, result: float) -> list[str]:
        p = self.input_data
        q3w, _, _ = self.find_Q_3W()
        k3w, _, _ = self.find_K_Г3W()
        n_total = p.a1 * p.a2 * p.a3
        x3_samples = [x for x in [p.k, p.k + 1, p.k + 2, n_total] if x <= n_total]
        sample_lines = []
        for x3 in x3_samples:
            seed = self._a3w_seed_term(x3)
            sample_lines.append(
                f"x3={x3}: x2_min={seed['x2_min']}, x1_min={seed['x1_min']}, "
                f"A=lambda1*x1+lambda2*x2={self._fmt_number(float(seed['A']))}, "
                f"B=lambda3*x3={self._fmt_number(float(seed['B']))}, "
                f"M=B*beta*t^(beta-1)+lambda0+A={self._fmt_number(float(seed['multiplier']))}, "
                f"inner=M*exp(-A*t)*exp(-B*t^beta)={self._fmt_number(float(seed['inner']))}, "
                f"seed=exp(-lambda0*t)*coef*inner={self._fmt_number(float(seed['seed']))}"
            )
        steps = [
            f"1) Підставлено в a_3W(k,t): k={p.k}, t={self._fmt_number(p.t)}.",
            f"2) Проміжні значення для поточного t: K_Г3W={self._fmt_number(k3w)}, Q_3W={self._fmt_number(q3w)}.",
            f"3) Параметри розподілу 3-го рівня: lambda3={self._fmt_number(p.lambda3)}, beta={self._fmt_number(p.beta)}.",
            f"4) Зовнішня сума для a_3W виконується за x3 від k={p.k} до N={n_total}.",
            "5) Деталізація seed-внесків для вибраних x3:",
        ]
        for line in sample_lines:
            steps.append(f"   - {line}")
        steps.append(f"6) Після повної багаторівневої суми отримано a_3W={self._fmt_number(result)}.")
        return steps

    def _steps_for_lambda3w(self, result: float) -> list[str]:
        a3w, _, _ = self.find_a_3W()
        k_h3w, _, _ = self.find_K_Г3W()
        ratio = a3w / k_h3w if abs(k_h3w) >= 1e-12 else float("inf")
        return [
            "1) Використано формулу lambda_3W = a_3W / K_Г3W.",
            f"2) Проміжні значення: a_3W={self._fmt_number(a3w)}, K_Г3W={self._fmt_number(k_h3w)}.",
            f"3) Арифметика: {self._fmt_number(a3w)} / {self._fmt_number(k_h3w)} = {self._fmt_number(ratio)}.",
            f"4) Підсумок: lambda_3W={self._fmt_number(result)}.",
        ]

    def clear_cache(self) -> bool:
        return self.cache.clear()