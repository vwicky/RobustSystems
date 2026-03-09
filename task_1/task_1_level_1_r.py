import math
from scipy.special import erfc
from dataclasses import dataclass
from abc import ABC, abstractmethod

class MathHandler:
    @staticmethod
    def combinations(n: int, k: int) -> int:
        if k < 0 or k > n:
            return 0
        return math.comb(n, k)

    @staticmethod
    def W(D1: float, D2: float) -> float:
        """Compute W(D1, D2) as per T_1R formula"""
        if D1 == 0:
            return float('inf')
        factor = math.sqrt(math.pi / (2 * D1))
        expo = math.exp(D2**2 / (2 * D1))
        erfc_val = erfc(D2 / math.sqrt(2 * D1))
        return factor * expo * erfc_val
    
    @staticmethod
    def format_float(val: float, decimals: int = 3) -> str:
        """
        Formats floats to a readable decimal (e.g., 0.658) 
        and only uses scientific notation when the number is very small.
        """
        if val == 0:
            return f"{0:.{decimals}f}"
        if abs(val) < 10**(-decimals):
            return f"{val:.{decimals}e}"
        return f"{val:.{decimals}f}"

@dataclass
class Task1_Level1_Parameters:
    a1: int
    sigma1: float
    lambda0: float

class Task1_Level1_T1R(ABC):
    def __init__(self, parameters: Task1_Level1_Parameters):
        self.parameters = parameters

    def solve(self) -> None:
        p = self.parameters
        print(f"Solving T_1R(x1) with parameters: a1={p.a1}, sigma1={p.sigma1}, lambda0={p.lambda0}\n")

        for x1 in range(1, p.a1 + 1):  # start from 1 to avoid infinity
            print(f"--- Computing T_1R({x1}) ---")
            c_a1_x1 = MathHandler.combinations(p.a1, x1)
            print(f"Combination(a1={p.a1}, x1={x1}) = {c_a1_x1}")

            t1r_value = 0.0

            for j1 in range(0, p.a1 - x1 + 1):
                c_a1_minus_x1_j1 = MathHandler.combinations(p.a1 - x1, j1)
                sign = (-1) ** j1
                D1 = (x1 + j1) / (p.sigma1 ** 2)
                W_val = MathHandler.W(D1, p.lambda0)
                term = c_a1_minus_x1_j1 * sign * W_val
                t1r_value += term

                print(f"  j1={j1}: Combination({p.a1 - x1}, {j1}) = {c_a1_minus_x1_j1}, "
                      f"Sign = {sign}, D1 = {MathHandler.format_float(D1)}, "
                      f"W(D1, lambda0) = {MathHandler.format_float(W_val)}, Term = {MathHandler.format_float(term)}")
                print(f"    Partial Sum = {MathHandler.format_float(t1r_value)}")
                print()

            t1r_value *= c_a1_x1
            print(f"T_1R({x1}) = {MathHandler.format_float(t1r_value, 6)}\n")
        print("-" * 50)


def main() -> None:
    parameters = Task1_Level1_Parameters(
        a1=5,
        sigma1=920,  # год
        lambda0=10 ** -4
    )

    # Calculate mean time T_1R
    task1_time = Task1_Level1_T1R(parameters)
    task1_time.solve()

if __name__ == "__main__":
    main()