import math
import scipy.integrate as spi
from abc import ABC, abstractmethod
from dataclasses import dataclass

class MathHandler:
    @staticmethod
    def combinations(n: int, k: int) -> int:
        """
        Calculates the number of ways to choose k elements 
        from a set of n elements without replacement and without order.
        """
        if k < 0 or k > n:
            return 0
        return math.comb(n, k)
    
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

    @staticmethod
    def calculate_integral(x1: int, j1: int, lambda0: float, lambda1: float, beta1: float) -> float:
        """
        Numerically calculates the integral from 0 to infinity for the T_1W function.
        """
        def integrand(t: float) -> float:
            try:
                # Об'єднаний показник експоненти: -lambda1*(x1+j1)*t^beta1 - lambda0*t
                exponent = -lambda1 * (x1 + j1) * (t ** beta1) - (lambda0 * t)
                return math.exp(exponent)
            except OverflowError:
                # Якщо t стає занадто великим, функція прямує до 0
                return 0.0

        # quad повертає (result, error), нас цікавить лише result
        result, _ = spi.quad(integrand, 0, math.inf)
        return result

class Equation(ABC):
    @abstractmethod
    def solve(self):
        pass

@dataclass
class Task1_Level1_Parameters:
    a1: int 
    lambda0: float
    lambda1: float
    t: int
    beta1: float

class Task1_Level1_P1W(Equation):
    def __init__(self, parameters: Task1_Level1_Parameters):
        self.parameters = parameters

    def solve_part1(self, x: int) -> int:
        return MathHandler.combinations(self.parameters.a1, x)
    
    def solve_part2(self) -> float:
        return math.exp(-self.parameters.lambda0 * self.parameters.t)
    
    def solve_part3(self, x: int) -> float:
        return math.exp(-self.parameters.lambda1 * x * (self.parameters.t ** self.parameters.beta1))
    
    def solve_part4(self, x: int) -> float:
        exponent = -self.parameters.lambda1 * (self.parameters.t ** self.parameters.beta1)
        base = -math.expm1(exponent) 
        return base ** (self.parameters.a1 - x)

    def solve(self) -> None:
        p = self.parameters
        print(f"Solving Task 1 Level 1 (Probability) with parameters: t={p.t}, a1={p.a1}\n")

        for x in range(0, p.a1 + 1):
            part1 = self.solve_part1(x)
            part2 = self.solve_part2()
            part3 = self.solve_part3(x)
            part4 = self.solve_part4(x)

            probability = part1 * part2 * part3 * part4
            
            print(f"P_1W({x}, {p.t}) = {MathHandler.format_float(probability)}")
            print(f"\tCombination ({x}; {p.a1}) = {part1}")
            print(f"\te^({-p.lambda0} * {p.t}) = {MathHandler.format_float(part2)}")
            print(f"\te^({-p.lambda1} * {x} * {p.t}^{p.beta1}) = {MathHandler.format_float(part3)}")
            print(f"\t(1 - e^({-p.lambda1} * {p.t}^{p.beta1}))^({p.a1} - {x}) = {MathHandler.format_float(part4)}")
            print()
        print("-" * 50)
        return probability


class Task1_Level1_T1W(Equation):
    def __init__(self, parameters: Task1_Level1_Parameters):
        self.parameters = parameters

    def solve(self) -> None:
        p = self.parameters
        # t is not printed here because the integral is calculated over t
        print(f"Solving T_1W(x1) (Mean Time) with parameters: a1={p.a1}, lambda0={p.lambda0}, lambda1={p.lambda1}, beta1={p.beta1}\n")

        for x1 in range(0, p.a1 + 1):
            # Зауважимо, що T_1W(0) = ∞
            if x1 == 0:
                print(f"T_1W({x1}) = ∞ (Infinity)\n")
                continue

            t1w_value = 0.0
            c_a1_x1 = MathHandler.combinations(p.a1, x1)

            print(f"\tCombination ({x1}; {p.a1}) = {c_a1_x1}")

            # Сума від j1 = 0 до a1 - x1
            for j1 in range(0, p.a1 - x1 + 1):
                c_a1_minus_x1_j1 = MathHandler.combinations(p.a1 - x1, j1)
                print(f"\t\tCombination ({j1}; {p.a1 - x1}) = {c_a1_minus_x1_j1}")
                sign = (-1) ** j1
                print(f"\t\tSign = {sign}")
                integral_val = MathHandler.calculate_integral(x1, j1, p.lambda0, p.lambda1, p.beta1)
                print(f"\t\tIntegral({x1}, {j1}) = {MathHandler.format_float(integral_val)}")

                term = c_a1_minus_x1_j1 * sign * integral_val
                t1w_value += term

            print(f"\tSum for x1={x1} = {MathHandler.format_float(t1w_value)}")
            
            # Множимо результат суми на біноміальний коефіцієнт перед сумою
            t1w_value *= c_a1_x1
            
            # Збільшив кількість знаків після коми для T_1W, оскільки час може бути досить великим
            print(f"T_1W({x1}) = {MathHandler.format_float(t1w_value, 2)}")
            print()
        print("-" * 50)


def main() -> None:
    parameters = Task1_Level1_Parameters(
        a1=5,
        lambda0=2 * 10 ** -4,
        lambda1=2 * 10 ** -4,
        t=100,
        beta1=1.3
    )
    
    # 1. Розрахунок ймовірностей (P_1W)
    #task1_prob = Task1_Level1_P1W(parameters)
    #task1_prob.solve()

    # 2. Розрахунок середнього часу (T_1W)
    task1_time = Task1_Level1_T1W(parameters)
    task1_time.solve()

if __name__ == "__main__":
    main()