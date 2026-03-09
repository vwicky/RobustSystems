import sys
from PyQt5.QtWidgets import QApplication

from src.solver_module import SolverModule
from src.gui_module import GUIModule
from src.input_dataclass import InputData, var_6

def main() -> None:
    app = QApplication(sys.argv)
    
    input_data_6: InputData = var_6

    solver_module = SolverModule(input_data_6)
    gui_module = GUIModule(solver_module)
    gui_module.run()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()