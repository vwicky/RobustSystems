from typing import Any
from matplotlib.figure import Figure

from src.input_dataclass import InputData
from src.solve_calculator import SolverCalculator

class SolverModule:
    def __init__(self, input_data: InputData):
        self.input_data = input_data
        self.calculator = SolverCalculator(input_data)

    def solve_pipeline(self, pipeline: dict[str, Any]) -> dict[str, dict]:
        solved_values = {}
        for key, func in pipeline.items():
            result, elapsed_time, error = self.calculator.check_time(func)
            
            if result is not None:
                if len(result) == 3:
                    value, solving_str, steps = result
                else:
                    value, solving_str = result
                    steps = []
            else:
                value, solving_str, steps = None, "", []

            # Return a structured dictionary for the GUI
            solved_values[key] = {
                "value": value,
                "latex": solving_str,
                "steps": steps,
                "time": elapsed_time,
                "error": str(error) if error else None,
            }
        return solved_values

    def task_1(self) -> dict:
        pipeline = {
            "P_3W": self.calculator.find_P_3W,
            "K_Г3W": self.calculator.find_K_Г3W,
            "Q_3W": self.calculator.find_Q_3W, # Replaced 1 - K_Г3W with Q_3W
            "T_3W": self.calculator.find_T_3W,
            "T_Г3W": self.calculator.find_T_Г3W,
        }
        return self.solve_pipeline(pipeline)

    def task_2(self) -> dict:
        pipeline = {
            "Q_3W": self.calculator.find_Q_3W,
            "a_3W": self.calculator.find_a_3W,
            "lambda_3W": self.calculator.find_lambda_3W,
        }
        return self.solve_pipeline(pipeline)
    
    def task_3(self) -> Figure:
        """ Interactive 3W Plots dynamically generated from input_data """
        import numpy as np
        from matplotlib.figure import Figure
        from matplotlib.widgets import Slider
        
        # 1. Import our hidden vectorized formulas
        from src.formulas.plot_3w_vec import q_3w_vec, a_3w_vec, lambda_3w_vec
        
        # 2. Grab all parameters directly from input_data
        p = self.input_data
        
        # Initial parameters for Level 1 & 2 (a1 and a2 get sliders now!)
        a1_init = p.a1
        a2_init = p.a2
        a3_init = p.a3

        # Keep plotting model aligned with InputData fields (single source of truth).
        k1 = min(p.k, a1_init)
        k2 = min(p.k, a2_init)
        k3_init = min(p.k, a3_init)
        l1, l2, l3_init = p.lambda1, p.lambda2, p.lambda3
        b1 = b2 = b3_init = p.beta
        l0_init = p.lambda0

        # 3. Determine which plots to draw based on input_data.plots
        allowed_plots = ["Q_3W", "a_3W", "lambda_3W"]
        requested_plots = [plot for plot in getattr(p, 'plots', []) if plot in allowed_plots]
        
        if not requested_plots:
            requested_plots = ["Q_3W", "a_3W"]

        num_plots = len(requested_plots)
        t_vals = np.linspace(0.1, 1000, 1200)

        # 4. Calculate initial data instantly
        q_init = q_3w_vec(t_vals, a1_init, k1, l1, b1, a2_init, k2, l2, b2, a3_init, k3_init, l3_init, b3_init, l0_init)
        a_init = a_3w_vec(t_vals, q_init)
        lam_init = lambda_3w_vec(t_vals, a_init, q_init)

        plot_config = {
            "Q_3W": (q_init, 'darkorange', r"Ймовірність відмови $Q_{3W}(t)$", r"Ймовірність $Q$"),
            "a_3W": (a_init, 'forestgreen', r"Щільність відмов $a_{3W}(t)$", r"Щільність $a$"),
            "lambda_3W": (lam_init, 'crimson', r"Інтенсивність відмов $\lambda_{3W}(t)$", r"Інтенсивність $\lambda$")
        }

        # 5. Build the UI Figure dynamically
        fig = Figure(figsize=(10, 3 * num_plots + 2))
        
        # INCREASED BOTTOM MARGIN TO 0.45 TO FIT 7 SLIDERS
        fig.subplots_adjust(bottom=0.45, hspace=0.4)

        axes_dict = {}
        lines_dict = {}

        for i, plot_name in enumerate(requested_plots):
            ax = fig.add_subplot(num_plots, 1, i + 1)
            init_data, color, title, ylabel = plot_config[plot_name]
            
            line, = ax.plot(t_vals, init_data, lw=2, color=color)
            
            ax.set_title(title)
            ax.set_ylabel(ylabel)
            ax.grid(True, linestyle='--', alpha=0.6)
            
            if plot_name == "Q_3W":
                ax.set_ylim(-0.05, 1.05)
            
            if i == num_plots - 1:
                ax.set_xlabel("Час (t), год")
                
            axes_dict[plot_name] = ax
            lines_dict[plot_name] = line

        # 6. Build the Sliders (Added ax_a1 and ax_a2)
        ax_color = 'lightgoldenrodyellow'
        ax_a1 = fig.add_axes([0.2, 0.30, 0.65, 0.02], facecolor=ax_color)
        ax_a2 = fig.add_axes([0.2, 0.26, 0.65, 0.02], facecolor=ax_color)
        ax_a3 = fig.add_axes([0.2, 0.22, 0.65, 0.02], facecolor=ax_color)
        ax_k3 = fig.add_axes([0.2, 0.18, 0.65, 0.02], facecolor=ax_color)
        ax_l3 = fig.add_axes([0.2, 0.14, 0.65, 0.02], facecolor=ax_color)
        ax_b3 = fig.add_axes([0.2, 0.10, 0.65, 0.02], facecolor=ax_color)
        ax_l0 = fig.add_axes([0.2, 0.06, 0.65, 0.02], facecolor=ax_color)

        s_a1 = Slider(ax_a1, r'$a_1$ (елем. Р1)', 1, 100, valinit=a1_init, valstep=1)
        s_a2 = Slider(ax_a2, r'$a_2$ (елем. Р2)', 1, 100, valinit=a2_init, valstep=1)
        s_a3 = Slider(ax_a3, r'$a_3$ (елем. Р3)', 1, 100, valinit=a3_init, valstep=1)
        s_k3 = Slider(ax_k3, r'$k_3$ (поріг Р3)', 1, a3_init, valinit=k3_init, valstep=1)
        s_l3 = Slider(ax_l3, r'$\lambda_3$', 0.000001, 0.01, valinit=l3_init, valfmt='%.6f')
        s_b3 = Slider(ax_b3, r'$\beta_3$ (форма)', 0.3, 6.0, valinit=b3_init)
        s_l0 = Slider(ax_l0, r'$\lambda_0$ (зовн.)', 0.000001, 0.01, valinit=l0_init, valfmt='%.6f')

        # 7. Update logic triggered by sliders
        def update(val):
            a1_val = s_a1.val
            a2_val = s_a2.val
            a3_val, l3_val, b3_val, l0_val = s_a3.val, s_l3.val, s_b3.val, s_l0.val

            # Keep k3 slider range synchronized when a3 changes.
            s_k3.valmax = a3_val
            s_k3.ax.set_xlim(s_k3.valmin, a3_val)
            
            # Constraint for Level 3
            current_k3 = s_k3.val
            if current_k3 > a3_val:
                s_k3.set_val(a3_val)
                current_k3 = a3_val
                
            # Recalculate arrays with dynamic a1 and a2!
            new_q = q_3w_vec(t_vals, a1_val, k1, l1, b1, a2_val, k2, l2, b2, a3_val, current_k3, l3_val, b3_val, l0_val)
            new_a = a_3w_vec(t_vals, new_q)
            new_lam = lambda_3w_vec(t_vals, new_a, new_q)
            
            data_map = {"Q_3W": new_q, "a_3W": new_a, "lambda_3W": new_lam}

            for pname in requested_plots:
                lines_dict[pname].set_ydata(data_map[pname])
                axes_dict[pname].relim()
                axes_dict[pname].autoscale_view(scalex=False)
                
            fig.canvas.draw_idle()

        # Connect the new sliders to the update loop
        s_a1.on_changed(update)
        s_a2.on_changed(update)
        s_a3.on_changed(update)
        s_k3.on_changed(update)
        s_l3.on_changed(update)
        s_b3.on_changed(update)
        s_l0.on_changed(update)

        # Protect against garbage collection
        fig._sliders = [s_a1, s_a2, s_a3, s_k3, s_l3, s_b3, s_l0]
        fig._update_func = update

        return fig

    def clear_cache(self) -> bool:
        return self.calculator.clear_cache()

    def console_solve(self) -> None:
        tasks = [
            ("Task 1", self.task_1()),
            ("Task 2", self.task_2()),
        ]

        for title, result_set in tasks:
            print(f"\n{title}")
            print("-" * len(title))
            for metric, payload in result_set.items():
                if payload.get("error"):
                    print(f"{metric}: ERROR -> {payload['error']}")
                    continue
                print(f"{metric}: {payload['value']} (time: {payload['time']:.4f}s)")

    def task_4(self) -> Figure:
        """ Draw the HBS (ІРС) tree and the representative series-parallel RBD """
        import networkx as nx
        from matplotlib.figure import Figure
        
        # Create a taller figure to stack both diagrams cleanly
        fig = Figure(figsize=(12, 11))
        fig.subplots_adjust(hspace=0.3, left=0.05, right=0.95)
        
        # Grab branching parameters safely
        a1 = getattr(self.input_data, 'a1', 3)
        a2 = getattr(self.input_data, 'a2', 3)
        a3 = getattr(self.input_data, 'a3', 3)
        
        # Visual limits: If a variant has 30 elements, drawing 30 parallel nodes becomes a black blob. 
        # We cap the visible drawn nodes at 3 and use "..." to represent the rest.
        v_a1, v_a2, v_a3 = min(a1, 3), min(a2, 3), min(a3, 3)

        # =========================================================
        # 1. Subplot 1: ІРС (Hierarchical Tree Diagram)
        # =========================================================
        ax1 = fig.add_subplot(2, 1, 1)
        ax1.set_title("1. Структурна схема ІРС (Ієрархічне дерево)", fontsize=14, fontweight="bold")
        ax1.axis('off')
        
        G_tree = nx.DiGraph()
        G_tree.add_node("0", layer=0, label="Ел. 0\n(Кореневий)")
        
        for i in range(v_a1):
            n1 = f"1_{i}"
            lbl1 = f"... до {a1}" if i == v_a1 - 1 and a1 > v_a1 else f"Ел. 1.{i+1}"
            G_tree.add_node(n1, layer=1, label=lbl1)
            G_tree.add_edge("0", n1)
            
            if i == 0:  # Expand only the first branch fully to show depth
                for j in range(v_a2):
                    n2 = f"2_{j}"
                    lbl2 = f"... до {a2}" if j == v_a2 - 1 and a2 > v_a2 else f"Ел. 2.{j+1}"
                    G_tree.add_node(n2, layer=2, label=lbl2)
                    G_tree.add_edge(n1, n2)
                    
                    if j == 0:
                        for k in range(v_a3):
                            n3 = f"3_{k}"
                            lbl3 = f"... до {a3}" if k == v_a3 - 1 and a3 > v_a3 else f"Ел. 3.{k+1}"
                            G_tree.add_node(n3, layer=3, label=lbl3)
                            G_tree.add_edge(n2, n3)

        # Layout top-down
        pos_tree = nx.multipartite_layout(G_tree, subset_key="layer", align="horizontal")
        pos_tree = {node: (x, -y) for node, (x, y) in pos_tree.items()} # Rotate 90 degrees
        labels_tree = nx.get_node_attributes(G_tree, 'label')
        
        nx.draw_networkx_edges(G_tree, pos_tree, ax=ax1, edge_color="#A0AEC0", width=1.5, arrows=True, node_size=2000)
        
        # Custom drawn nodes with circular bounding boxes
        for node, (x, y) in pos_tree.items():
            bbox = dict(boxstyle="circle,pad=0.3", fc="#E2E8F0", ec="#4A5568", lw=1.5)
            ax1.text(x, y, labels_tree[node], ha='center', va='center', fontsize=9, fontweight='bold', bbox=bbox, zorder=5)


        # =========================================================
        # 2. Subplot 2: Послідовно-паралельна схема (Series-Parallel RBD)
        # =========================================================
        ax2 = fig.add_subplot(2, 1, 2)
        ax2.set_title(f"2. Послідовно-паралельна схема резервування (a1={a1}, a2={a2}, a3={a3})", fontsize=14, fontweight="bold")
        ax2.axis('off')
        
        G_rbd = nx.DiGraph()
        G_rbd.add_node("IN", layer=0, label="Вхід")
        G_rbd.add_node("0", layer=1, label="Ел. 0")
        G_rbd.add_edge("IN", "0")
        G_rbd.add_node("OUT", layer=5, label="Вихід")
        
        leaf_nodes = []
        for i in range(v_a1):
            n1 = f"R1_{i}"
            lbl1 = f"... ({a1})" if i == v_a1 - 1 and a1 > v_a1 else f"Ел. 1.{i+1}"
            G_rbd.add_node(n1, layer=2, label=lbl1)
            G_rbd.add_edge("0", n1)
            
            if i == 0:
                for j in range(v_a2):
                    n2 = f"R2_{j}"
                    lbl2 = f"... ({a2})" if j == v_a2 - 1 and a2 > v_a2 else f"Ел. 2.{j+1}"
                    G_rbd.add_node(n2, layer=3, label=lbl2)
                    G_rbd.add_edge(n1, n2)
                    
                    if j == 0:
                        for k in range(v_a3):
                            n3 = f"R3_{k}"
                            lbl3 = f"... ({a3})" if k == v_a3 - 1 and a3 > v_a3 else f"Ел. 3.{k+1}"
                            G_rbd.add_node(n3, layer=4, label=lbl3)
                            G_rbd.add_edge(n2, n3)
                            leaf_nodes.append(n3)
                    else:
                        dummy_l3 = f"R3_dum_{j}"
                        G_rbd.add_node(dummy_l3, layer=4, label="...")
                        G_rbd.add_edge(n2, dummy_l3)
                        leaf_nodes.append(dummy_l3)
            else:
                dummy_l2 = f"R2_dum_{i}"
                dummy_l3 = f"R3_dum_{i}"
                G_rbd.add_node(dummy_l2, layer=3, label="...")
                G_rbd.add_node(dummy_l3, layer=4, label="...")
                G_rbd.add_edge(n1, dummy_l2)
                G_rbd.add_edge(dummy_l2, dummy_l3)
                leaf_nodes.append(dummy_l3)

        for leaf in leaf_nodes:
            G_rbd.add_edge(leaf, "OUT")

        # Layout left-to-right based on "layer" attribute
        pos_rbd = nx.multipartite_layout(G_rbd, subset_key="layer", align="vertical")
        labels_rbd = nx.get_node_attributes(G_rbd, 'label')
        
        nx.draw_networkx_edges(G_rbd, pos_rbd, ax=ax2, edge_color="#2D3436", width=2, arrows=True, node_size=2500, arrowsize=15)
        
        # Custom drawn nodes as rectangular blocks (RBD style)
        for node, (x, y) in pos_rbd.items():
            label = labels_rbd[node]
            if node in ["IN", "OUT"]:
                bbox = dict(boxstyle="circle,pad=0.3", fc="#55E6C1", ec="#2D3436", lw=1.5)
            else:
                bbox = dict(boxstyle="round,pad=0.5", fc="#FDCB6E", ec="#2D3436", lw=1.5)
            
            ax2.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold', bbox=bbox, zorder=5)

        # Metadata for GUI-side interactivity (click/pick info by subplot).
        fig._graph_data = {
            "layers": [
                {
                    "axis_index": 0,
                    "graph": G_tree,
                    "pos": pos_tree,
                    "labels": labels_tree,
                    "title": "ІРС (ієрархічне дерево)",
                },
                {
                    "axis_index": 1,
                    "graph": G_rbd,
                    "pos": pos_rbd,
                    "labels": labels_rbd,
                    "title": "Послідовно-паралельна схема (RBD)",
                },
            ]
        }

        return fig