from typing import Any

from PyQt5.QtCore import QThread, pyqtSignal


class ComputeWorker(QThread):
    started_run = pyqtSignal()
    progress = pyqtSignal(int)
    step_changed = pyqtSignal(str)
    finished = pyqtSignal(dict, dict, object, object)
    failed = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(self, solver_module: Any):
        super().__init__()
        self.solver = solver_module
        self._cancel_requested = False

    def request_cancel(self) -> None:
        self._cancel_requested = True

    def _check_cancel(self) -> bool:
        if self._cancel_requested:
            self.cancelled.emit()
            return True
        return False

    def run(self) -> None:
        try:
            self.started_run.emit()
            if self._check_cancel():
                return

            self.step_changed.emit("Обчислення завдання 1")
            self.progress.emit(10)
            t1_results = self.solver.task_1()
            if self._check_cancel():
                return

            self.step_changed.emit("Обчислення завдання 2")
            self.progress.emit(40)
            t2_results = self.solver.task_2()
            if self._check_cancel():
                return

            self.step_changed.emit("Побудова графіків завдання 3")
            self.progress.emit(70)
            t3_fig = self.solver.task_3()
            if self._check_cancel():
                return

            self.step_changed.emit("Побудова схеми завдання 4")
            self.progress.emit(90)
            t4_fig = self.solver.task_4()
            if self._check_cancel():
                return

            self.progress.emit(100)
            self.step_changed.emit("Завершено")
            self.finished.emit(t1_results, t2_results, t3_fig, t4_fig)
        except Exception as exc:
            self.failed.emit(str(exc))
