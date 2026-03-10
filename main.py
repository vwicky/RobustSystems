import argparse
import sys
from PyQt5.QtWidgets import QApplication

from src.color_themes import get_available_themes
from src.solver_module import SolverModule
from src.gui_module import GUIModule
from src.input_dataclass import InputData, var_6, var_17

def main() -> None:
    parser = argparse.ArgumentParser(description="RobustSmartSystems GUI")
    parser.add_argument(
        "--theme",
        default="light",
        choices=get_available_themes(),
        help="Color palette for the GUI.",
    )
    args = parser.parse_args()

    app = QApplication(sys.argv)
    
    input_data_17: InputData = var_17

    solver_module = SolverModule(input_data_17)
    gui_module = GUIModule(solver_module, theme_name=args.theme)
    gui_module.run()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()