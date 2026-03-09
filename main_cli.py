from src.solver_module import SolverModule
from src.input_dataclass import (
    InputData,
    var_6,
)


def main() -> None:
    input_data_6: InputData = var_6

    solver_module = SolverModule(input_data_6)

    solver_module.console_solve()


if __name__ == "__main__":
    main()