import argparse
import sys

# Select Qt backend before any matplotlib.figure / backend imports (avoids crashes on macOS).
import matplotlib

matplotlib.use("Qt5Agg")

from PyQt5.QtWidgets import QApplication

from src.color_themes import get_available_themes


def main() -> None:
    parser = argparse.ArgumentParser(description="RobustSmartSystems GUI")
    parser.add_argument(
        "--theme",
        default="light",
        choices=get_available_themes(),
        help="Color palette for the GUI.",
    )
    args = parser.parse_args()

    # QApplication must exist before matplotlib's Qt5Agg backend loads (avoids bus errors on macOS).
    app = QApplication(sys.argv)

    from src.gui_module import GUIModule
    from src.input_dataclass import InputData, var_17
    from src.solver_module import SolverModule

    input_data_6: InputData = var_17

    solver_module = SolverModule(input_data_6)
    gui_module = GUIModule(solver_module, theme_name=args.theme)
    gui_module.run()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()