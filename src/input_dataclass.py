from dataclasses import dataclass

@dataclass
class InputData:
    var_id: int

    a1: int
    a2: int
    a3: int

    k: int   # num. of total working components
    t: float # hours 

    lambda0: float
    lambda1: float
    lambda2: float
    lambda3: float

    beta: float

    plots: list[str]

    def __post_init__(self) -> None:
        total_components = self.a1 * self.a2 * self.a3

        if self.var_id < 0:
            raise ValueError("var_id must be non-negative.")

        for name in ("a1", "a2", "a3"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"{name} must be a positive integer.")

        if not (0 <= self.k <= total_components):
            raise ValueError(
                f"k must be in range [0, {total_components}] for a1*a2*a3={total_components}."
            )

        if self.t <= 0:
            raise ValueError("t must be positive.")

        for name in ("lambda0", "lambda1", "lambda2", "lambda3"):
            value = getattr(self, name)
            if value <= 0:
                raise ValueError(f"{name} must be positive.")

        if self.beta <= 0:
            raise ValueError("beta must be positive.")

        if not isinstance(self.plots, list):
            raise ValueError("plots must be a list[str].")

var_6 = InputData(
    var_id = 6,

    a1 = 5,
    a2 = 6,
    a3 = 7,

    k = 6,   # num. of total working components
    t = 1000.0, # hours 

    lambda0 = 2e-4, # 1 / hours
    lambda1 = 2e-4, # 1 / hours
    lambda2 = 3e-3, # 1 / hours
    lambda3 = 2e-4, # 1 / hours

    beta = 1.2, # changed from 1.3 to 1.2

    plots = ["Q_3W", "a_3W"]
)

var_15 = InputData(
    var_id = 17,

    a1 = 4, #4
    a2 = 7, #7
    a3 = 9, #9

    k = 8,   # num. of total working components 8
    t = 100.0, # hours 

    lambda0 = 2e-3, # 1 / hours
    lambda1 = 3e-3, # 1 / hours
    lambda2 = 2e-4, # 1 / hours
    lambda3 = 1e-4, # 1 / hours

    beta = 1.2, #1.2

    plots = ["a_3W", "lambda_3W"]
)

var_16 = InputData(
    var_id = 17,
    a1 = 4, a2 = 7, a3 = 9, # N = 252
    k = 200,
    t = 1000.0, 

    # Робимо lambda0 мінімальною, щоб вона не зміщувала графік вертикально
    lambda0 = 1e-7, 

    # КЛЮЧОВІ ЗМІНИ:
    # Збільшуємо відмови на рівнях 1 та 2, щоб вони "не тримали" структуру.
    # Коли lambda1 та lambda2 великі, ієрархічні піки зникають.
    lambda1 = 0.008, 
    lambda2 = 0.015, 
    
    # lambda3 має бути достатньою, щоб при t=1000 та beta=1.5 
    # ймовірність успіху p була < 0.05. Це дасть ідеальний спад.
    lambda3 = 0.0002, 

    beta = 1.5,
    plots = ["a_3W", "lambda_3W"]
)

var_17 = InputData(
    var_id = 17,
    a1 = 4, a2 = 7, a3 = 9, # N = 252
    k = 200,
    t = 1000.0, 

    # lambda0 має бути мінімальною, щоб не "притискати" весь графік до осі
    lambda0 = 1e-6, 

    # Збільшуємо інтенсивність відмов, щоб p (ймовірність успіху) була малою.
    # Коли p < 0.1, розподіл стає схожим на геометричний (спадаючий).
    lambda1 = 1e-3, 
    lambda2 = 2e-3, 
    lambda3 = 5e-5, # При t=1000 та beta=1.5 це дасть значний спад

    beta = 1.5,
    plots = ["a_3W", "lambda_3W"]
)