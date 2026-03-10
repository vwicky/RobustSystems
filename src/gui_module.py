import io

from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QShortcut,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

from src.gui_models import MetricResult, normalize_metrics
from src.gui_worker import ComputeWorker
from src.color_themes import build_stylesheet, get_theme_palette, rgba
from src.solver_module import SolverModule

METRIC_EXPLANATIONS_UA: dict[str, str] = {
    "P_3W": (
        "Ймовірність безвідмовної роботи P_n(X,t): базовий показник надійності. "
        "Показує ймовірність (0..1), що система в конфігурації X працює без поломки "
        "від 0 до часу t."
    ),
    "K_Г3W": (
        "Коефіцієнт готовності K_Γn(k,t): імовірність, що рівень системи лишається "
        "працездатним у момент t за умови резервування, коли для роботи достатньо "
        "щонайменше k справних елементів."
    ),
    "Q_3W": (
        "Ймовірність відмови. Для резервованого рівня це 1−K_Γn(k,t): імовірність, "
        "що до моменту t справними залишаться менше ніж k компонентів. На графіку "
        "Q(k,t) зростає з часом від 0 до 1."
    ),
    "T_3W": (
        "Середній час безвідмовної роботи T_n(X): математичне очікування часу "
        "роботи без відмови (площа під кривою P_n(X,t) на [0, +∞))."
    ),
    "T_Г3W": (
        "Середній час безвідмовної роботи з резервуванням T_Γn(k): середня "
        "тривалість життя резервованого рівня (площа під кривою K_Γn(k,t))."
    ),
    "a_3W": (
        "Щільність відмов a(k,t): швидкість зміни ймовірності відмови Q(k,t). "
        "Пік на графіку вказує на період найвищої концентрації відмов."
    ),
    "lambda_3W": (
        "Інтенсивність відмов λ(k,t)=a(t)/(1−Q(t)): умовна миттєва ймовірність "
        "відмови за умови, що система дожила до часу t. Для експоненційного закону "
        "зазвичай стала, для Вейбула/Релея зазвичай зростає через старіння."
    ),
}


class GUIModule(QMainWindow):
    def __init__(self, solver_module: SolverModule, theme_name: str = "light"):
        super().__init__()
        self.solver_module = solver_module
        self.theme_name = theme_name
        self.settings = QSettings("RobustSmartSystems", "ReliabilitySolver")
        self.worker: ComputeWorker | None = None
        self._latex_pixmap_cache: dict[str, QPixmap] = {}
        self._task4_info_label: QLabel | None = None
        self._task4_selected_artist = None

        self.setWindowTitle(f"Калькулятор надійності — Варіант {self.solver_module.input_data.var_id}")
        self.resize(1200, 900)
        self.apply_theme()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        root_layout = QVBoxLayout(self.central_widget)
        root_layout.setContentsMargins(14, 14, 14, 14)
        root_layout.setSpacing(12)

        self.splitter = QSplitter(Qt.Vertical)
        root_layout.addWidget(self.splitter)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        self.tabs = QTabWidget()
        top_layout.addWidget(self.tabs)
        self.splitter.addWidget(top_widget)

        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Журнал діагностики...")
        self.log_output.setMaximumHeight(180)
        self.splitter.addWidget(self.log_output)

        self.init_input_tab()
        self.init_task_tabs()
        self.setup_shortcuts()
        self.restore_ui_state()

    def apply_theme(self) -> None:
        self.setStyleSheet(build_stylesheet(self.theme_name))

    @property
    def _palette(self):
        return get_theme_palette(self.theme_name)

    def setup_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+R"), self, activated=self.start_computation)
        QShortcut(QKeySequence("Ctrl+L"), self, activated=self.clear_cache)
        QShortcut(QKeySequence("Ctrl+."), self, activated=self.request_cancel)
        QShortcut(QKeySequence("Ctrl+D"), self, activated=self.toggle_diagnostics)

    def restore_ui_state(self) -> None:
        geometry = self.settings.value("window/geometry")
        if geometry is not None:
            self.restoreGeometry(geometry)

        splitter_state = self.settings.value("window/splitter")
        if splitter_state is not None:
            self.splitter.restoreState(splitter_state)

        tab_index = self.settings.value("window/tab_index")
        if tab_index is not None:
            self.tabs.setCurrentIndex(int(tab_index))

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.settings.setValue("window/geometry", self.saveGeometry())
        self.settings.setValue("window/splitter", self.splitter.saveState())
        self.settings.setValue("window/tab_index", self.tabs.currentIndex())
        super().closeEvent(event)

    def log(self, message: str) -> None:
        self.log_output.appendPlainText(message)

    def toggle_diagnostics(self) -> None:
        self.log_output.setVisible(not self.log_output.isVisible())

    def get_distribution_info(self) -> str:
        rayleigh_variants = {1, 2, 3, 7, 8, 9, 13, 14, 15, 19, 20, 21, 25, 26, 27, 31, 32, 33, 37, 38, 39}
        return "Розподіл Релея" if self.solver_module.input_data.var_id in rayleigh_variants else "Розподіл Вейбула"

    @staticmethod
    def _create_param_row(icon_text: str, label: str, value: str) -> QWidget:
        row_widget = QWidget()
        row_widget.setObjectName("paramRow")
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(12, 8, 12, 8)
        row_layout.setSpacing(12)

        icon_label = QLabel(icon_text)
        icon_label.setObjectName("paramIcon")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(30, 30)

        key_label = QLabel(label)
        key_label.setObjectName("paramKey")
        key_label.setMinimumWidth(230)

        value_label = QLabel(value)
        value_label.setObjectName("paramValue")
        value_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        row_layout.addWidget(icon_label)
        row_layout.addWidget(key_label)
        row_layout.addWidget(value_label, 1)
        return row_widget

    def init_input_tab(self) -> None:
        self.input_tab = QWidget()
        layout = QVBoxLayout(self.input_tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        assignment_box = QGroupBox("Інформація про завдання")
        assignment_layout = QVBoxLayout(assignment_box)
        assignment_text = QLabel(
            "Модуль: надійність смарт-систем.\n"
            "Елементи 3-го рівня підпорядковуються закону розподілу за варіантом, "
            "а вищі рівні — експоненційному.\n"
            f"Варіант {self.solver_module.input_data.var_id}: {self.get_distribution_info()}."
        )
        assignment_text.setWordWrap(True)
        assignment_layout.addWidget(assignment_text)
        layout.addWidget(assignment_box)

        data = self.solver_module.input_data
        params_box = QGroupBox("Вхідні параметри системи")
        params_layout = QVBoxLayout(params_box)
        params_layout.setContentsMargins(8, 12, 8, 8)
        params_layout.setSpacing(8)
        params_layout.addWidget(self._create_param_row("ID", "ID варіанта", str(data.var_id)))
        params_layout.addWidget(
            self._create_param_row("A", "Компоненти (a1, a2, a3)", f"{data.a1}, {data.a2}, {data.a3}")
        )
        params_layout.addWidget(self._create_param_row("K", "Мінімум справних (k)", str(data.k)))
        params_layout.addWidget(self._create_param_row("T", "Час (t)", f"{data.t} год"))
        params_layout.addWidget(
            self._create_param_row("L", "Лямбда", f"{data.lambda0}, {data.lambda1}, {data.lambda2}, {data.lambda3}")
        )
        params_layout.addWidget(self._create_param_row("B", "Бета", str(data.beta)))
        layout.addWidget(params_box)

        controls = QHBoxLayout()
        controls.setSpacing(10)
        self.btn_compute = QPushButton("Обчислити результати (Ctrl+R)")
        self.btn_compute.clicked.connect(self.start_computation)
        self.btn_cancel = QPushButton("Скасувати (Ctrl+.)")
        self.btn_cancel.clicked.connect(self.request_cancel)
        self.btn_cancel.setEnabled(False)
        self.btn_cache = QPushButton("Очистити кеш (Ctrl+L)")
        self.btn_cache.setObjectName("dangerButton")
        self.btn_cache.clicked.connect(self.clear_cache)
        self.btn_toggle_logs = QPushButton("Показати/сховати діагностику (Ctrl+D)")
        self.btn_toggle_logs.clicked.connect(self.toggle_diagnostics)

        controls.addWidget(self.btn_cache)
        controls.addWidget(self.btn_toggle_logs)
        controls.addStretch()
        controls.addWidget(self.btn_cancel)
        controls.addWidget(self.btn_compute)
        layout.addLayout(controls)

        progress_row = QHBoxLayout()
        progress_row.setSpacing(10)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.status_label = QLabel("Очікування")
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.status_label)
        layout.addLayout(progress_row)

        self.tabs.addTab(self.input_tab, "Вхідні дані")

    def _create_results_tab(self, title: str) -> tuple[QScrollArea, QVBoxLayout]:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(12, 12, 12, 12)
        container_layout.setSpacing(10)
        container_layout.addStretch()

        area = QScrollArea()
        area.setWidgetResizable(True)
        area.setWidget(container)
        self.tabs.addTab(area, title)
        return area, container_layout

    def init_task_tabs(self) -> None:
        self.task1_tab, self.task1_layout = self._create_results_tab("1. Основні характеристики")
        self.task2_tab, self.task2_layout = self._create_results_tab("2. Умова готовності")
        self.task3_tab, self.task3_layout = self._create_results_tab("3. Графіки")
        self.task4_tab, self.task4_layout = self._create_results_tab("4. Архітектура")

    def start_computation(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            QMessageBox.information(self, "Обчислення", "Обчислення вже виконується.")
            return

        self.progress_bar.setValue(0)
        self.status_label.setText("Запуск")
        self.btn_compute.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        self.worker = ComputeWorker(self.solver_module)
        self.worker.started_run.connect(lambda: self.log("[worker] run started"))
        self.worker.step_changed.connect(self._on_step_changed)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.on_computation_finished)
        self.worker.failed.connect(self.on_computation_failed)
        self.worker.cancelled.connect(self.on_computation_cancelled)
        self.worker.start()

    def request_cancel(self) -> None:
        if self.worker is not None and self.worker.isRunning():
            self.log("[worker] cancellation requested")
            self.worker.request_cancel()
            self.status_label.setText("Скасування...")

    def _on_step_changed(self, step_name: str) -> None:
        self.status_label.setText(step_name)
        self.log(f"[worker] {step_name}")

    def clear_cache(self) -> None:
        ok = bool(self.solver_module.clear_cache())
        if ok:
            QMessageBox.information(self, "Кеш", "Кеш успішно очищено.")
            self.log("[cache] cache cleared")
        else:
            QMessageBox.warning(self, "Кеш", "Не вдалося очистити кеш.")
            self.log("[cache] failed to clear cache")

    @staticmethod
    def _build_value_widget(value) -> QWidget:
        if isinstance(value, (int, float)):
            label = QLabel(f"{value:.6g}")
            label.setStyleSheet("font: 700 20px 'Consolas';")
            return label

        if isinstance(value, (list, tuple)):
            table = QTableWidget(len(value), 2)
            table.setHorizontalHeaderLabels(["Індекс", "Значення"])
            table.verticalHeader().setVisible(False)
            for i, item in enumerate(value):
                table.setItem(i, 0, QTableWidgetItem(str(i)))
                item_text = f"{item:.6g}" if isinstance(item, float) else str(item)
                table.setItem(i, 1, QTableWidgetItem(item_text))
            table.setMaximumHeight(280)
            table.resizeColumnsToContents()
            return table

        if isinstance(value, dict):
            table = QTableWidget(len(value), 2)
            table.setHorizontalHeaderLabels(["Ключ", "Значення"])
            table.verticalHeader().setVisible(False)
            for row, (k, v) in enumerate(value.items()):
                table.setItem(row, 0, QTableWidgetItem(str(k)))
                value_text = f"{v:.6g}" if isinstance(v, float) else str(v)
                table.setItem(row, 1, QTableWidgetItem(value_text))
            table.resizeColumnsToContents()
            return table

        fallback = QLabel(str(value))
        fallback.setWordWrap(True)
        return fallback

    def _create_metric_card(self, metric: MetricResult) -> QGroupBox:
        card = QGroupBox(metric.name)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(8)

        time_label = QLabel(f"Час обчислення: {metric.elapsed_seconds:.4f} с")
        time_label.setStyleSheet(f"color: {rgba(self._palette.text, 0.65)};")
        layout.addWidget(time_label)

        if metric.latex:
            formula_title = QLabel("Формула")
            formula_title.setStyleSheet(f"font-weight: 700; color: {self._palette.accent};")
            formula_value = self._build_latex_widget(metric.latex)
            layout.addWidget(formula_title)
            layout.addWidget(formula_value)

        explanation = METRIC_EXPLANATIONS_UA.get(metric.name)
        if explanation:
            explanation_title = QLabel("Пояснення")
            explanation_title.setStyleSheet(f"font-weight: 700; color: {self._palette.accent};")
            explanation_body = QLabel(explanation)
            explanation_body.setWordWrap(True)
            explanation_body.setStyleSheet(
                f"background: {rgba(self._palette.card_bg, 0.78)}; "
                f"border-left: 3px solid {rgba(self._palette.border, 0.95)}; padding: 8px;"
            )
            layout.addWidget(explanation_title)
            layout.addWidget(explanation_body)

        result_title = QLabel("Результат")
        result_title.setStyleSheet(f"font-weight: 700; color: {self._palette.accent};")
        layout.addWidget(result_title)

        if metric.error:
            error_label = QLabel(metric.error)
            error_label.setWordWrap(True)
            error_label.setStyleSheet(
                f"background: {rgba(self._palette.danger, 0.16)}; "
                f"border-left: 3px solid {self._palette.danger}; color: {self._palette.danger_pressed}; padding: 8px;"
            )
            layout.addWidget(error_label)
        else:
            layout.addWidget(self._build_value_widget(metric.value))

        if metric.steps:
            toggle_button = QToolButton()
            toggle_button.setCheckable(True)
            toggle_button.setChecked(False)
            toggle_button.setText("Показати покроковий розв'язок")
            toggle_button.setArrowType(Qt.RightArrow)
            toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

            steps_box = QPlainTextEdit()
            steps_box.setReadOnly(True)
            steps_box.setPlainText("\n".join(metric.steps))
            steps_box.setVisible(False)
            steps_box.setMaximumHeight(180)
            steps_box.setStyleSheet(
                f"background: {rgba(self._palette.card_bg, 0.72)}; "
                f"border: 1px solid {rgba(self._palette.border, 0.9)}; border-radius: 6px; "
                f"padding: 6px; color: {self._palette.text};"
            )

            def toggle_steps(checked: bool) -> None:
                steps_box.setVisible(checked)
                toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
                toggle_button.setText(
                    "Сховати покроковий розв'язок" if checked else "Показати покроковий розв'язок"
                )

            toggle_button.toggled.connect(toggle_steps)
            layout.addWidget(toggle_button)
            layout.addWidget(steps_box)

        return card

    def _build_latex_widget(self, latex_str: str) -> QWidget:
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(8, 8, 8, 8)
        container_layout.setSpacing(4)

        img_label = QLabel()
        img_label.setStyleSheet(
            f"background: {rgba(self._palette.card_bg, 0.72)}; "
            f"border-left: 3px solid {self._palette.accent}; padding: 8px;"
        )
        img_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        pixmap = self._render_latex_pixmap(latex_str)
        if pixmap is not None:
            img_label.setPixmap(pixmap)
            img_label.setToolTip(latex_str)
        else:
            img_label.setText(latex_str)
            img_label.setWordWrap(True)
            img_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        container_layout.addWidget(img_label)
        return container

    def _render_latex_pixmap(self, latex_str: str) -> QPixmap | None:
        if latex_str in self._latex_pixmap_cache:
            return self._latex_pixmap_cache[latex_str]

        normalized = latex_str.strip().replace(r"\limits", "").replace(r"\displaystyle", "")
        if not normalized:
            return None
        if not normalized.startswith("$"):
            normalized = f"${normalized}$"

        fig = Figure(figsize=(6, 0.7), dpi=160)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        ax.axis("off")
        fig.patch.set_alpha(0.0)

        try:
            ax.text(0.01, 0.5, normalized, fontsize=12, ha="left", va="center")
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", transparent=True, pad_inches=0.05)
            data = buf.getvalue()
            pix = QPixmap()
            if not pix.loadFromData(data):
                return None
            self._latex_pixmap_cache[latex_str] = pix
            return pix
        except Exception:
            return None
        finally:
            fig.clf()

    def _populate_result_layout(self, target_layout: QVBoxLayout, payload: dict[str, dict]) -> None:
        self.clear_layout(target_layout)
        metrics = normalize_metrics(payload)
        if not metrics:
            target_layout.addWidget(QLabel("Результатів немає."))
            target_layout.addStretch()
            return

        for metric in metrics:
            target_layout.addWidget(self._create_metric_card(metric))
        target_layout.addStretch()

    def on_computation_finished(self, t1: dict, t2: dict, f3, f4) -> None:
        self.btn_compute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText("Завершено")
        self.log("[worker] completed successfully")

        self._populate_result_layout(self.task1_layout, t1)
        self._populate_result_layout(self.task2_layout, t2)

        self.clear_layout(self.task3_layout)
        canvas3 = FigureCanvas(f3)
        toolbar3 = NavigationToolbar(canvas3, self)
        canvas3.setMinimumSize(800, 600)
        self.task3_layout.addWidget(toolbar3)
        self.task3_layout.addWidget(canvas3)
        self.task3_layout.addStretch()

        self.clear_layout(self.task4_layout)
        canvas4 = FigureCanvas(f4)
        toolbar4 = NavigationToolbar(canvas4, self)
        self._task4_info_label = QLabel("Інтерактивність: клікніть вузол для деталей, колесо миші для масштабування.")
        self._task4_info_label.setWordWrap(True)
        self._task4_info_label.setStyleSheet(
            f"background: {rgba(self._palette.card_bg, 0.76)}; "
            f"border: 1px solid {rgba(self._palette.border, 0.9)}; border-radius: 6px; "
            f"padding: 8px; color: {self._palette.text};"
        )
        self.task4_layout.addWidget(self._task4_info_label)
        self.task4_layout.addWidget(toolbar4)
        self.task4_layout.addWidget(canvas4)
        self._setup_task4_interactions(canvas4, f4)
        self.task4_layout.addStretch()

    def on_computation_failed(self, error_message: str) -> None:
        self.btn_compute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText("Помилка")
        self.log(f"[worker] failed: {error_message}")
        QMessageBox.critical(self, "Помилка обчислення", error_message)

    def on_computation_cancelled(self) -> None:
        self.btn_compute.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.status_label.setText("Скасовано")
        self.log("[worker] cancelled")

    @staticmethod
    def clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _setup_task4_interactions(self, canvas: FigureCanvas, fig) -> None:
        graph_data = getattr(fig, "_graph_data", None)
        if not graph_data:
            return

        layers = graph_data.get("layers")
        if not layers:
            return

        def on_click(event) -> None:
            if event.inaxes is None or event.xdata is None or event.ydata is None:
                return

            active_layer = self._layer_for_axis(event.inaxes, fig, layers)
            if active_layer is None:
                return

            graph = active_layer["graph"]
            pos = active_layer["pos"]
            labels = active_layer.get("labels", {})
            layer_title = active_layer.get("title", "Схема")

            clicked_node = self._nearest_node(event.xdata, event.ydata, pos, event.inaxes)
            if clicked_node is None:
                return

            self._highlight_task4_node(event.inaxes, pos, clicked_node, canvas)
            self._update_task4_node_info(graph, clicked_node, labels, layer_title)

        def on_scroll(event) -> None:
            if event.inaxes is None or event.xdata is None or event.ydata is None:
                return
            self._zoom_axis(event.inaxes, event.xdata, event.ydata, event.button)
            canvas.draw_idle()

        canvas.mpl_connect("button_press_event", on_click)
        canvas.mpl_connect("scroll_event", on_scroll)

    @staticmethod
    def _layer_for_axis(axis, fig, layers: list[dict]) -> dict | None:
        for layer in layers:
            axis_index = layer.get("axis_index")
            if isinstance(axis_index, int) and axis_index < len(fig.axes) and fig.axes[axis_index] is axis:
                return layer
        return None

    def _nearest_node(self, x: float, y: float, pos: dict, ax) -> str | None:
        x0, x1 = ax.get_xlim()
        y0, y1 = ax.get_ylim()
        scale = max(abs(x1 - x0), abs(y1 - y0))
        threshold = 0.06 * scale
        threshold_sq = threshold * threshold

        best_node = None
        best_dist = None
        for node, (nx_val, ny_val) in pos.items():
            dx = nx_val - x
            dy = ny_val - y
            dist_sq = dx * dx + dy * dy
            if dist_sq <= threshold_sq and (best_dist is None or dist_sq < best_dist):
                best_dist = dist_sq
                best_node = node
        return best_node

    def _highlight_task4_node(self, ax, pos: dict, node: str, canvas: FigureCanvas) -> None:
        if self._task4_selected_artist is not None:
            self._task4_selected_artist.remove()
            self._task4_selected_artist = None

        x, y = pos[node]
        self._task4_selected_artist = ax.scatter(
            [x],
            [y],
            s=3000,
            facecolors="none",
            edgecolors="#DC2626",
            linewidths=2.5,
            zorder=10,
        )
        canvas.draw_idle()

    def _update_task4_node_info(self, graph, node: str, labels: dict[str, str], layer_title: str) -> None:
        if self._task4_info_label is None:
            return
        out_degree = graph.out_degree(node)
        in_degree = graph.in_degree(node)
        display_name = labels.get(node, node)
        self._task4_info_label.setText(
            f"Схема: {layer_title}\n"
            f"Вибраний вузол: {display_name} ({node})\n"
            f"Вхідних зв'язків: {in_degree} | Вихідних зв'язків: {out_degree}"
        )

    @staticmethod
    def _zoom_axis(ax, x: float, y: float, direction: str) -> None:
        base_scale = 1.2
        scale_factor = 1 / base_scale if direction == "up" else base_scale

        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()

        new_width = (x_max - x_min) * scale_factor
        new_height = (y_max - y_min) * scale_factor

        relx = (x_max - x) / (x_max - x_min) if x_max != x_min else 0.5
        rely = (y_max - y) / (y_max - y_min) if y_max != y_min else 0.5

        ax.set_xlim([x - new_width * (1 - relx), x + new_width * relx])
        ax.set_ylim([y - new_height * (1 - rely), y + new_height * rely])

    def run(self) -> None:
        self.show()