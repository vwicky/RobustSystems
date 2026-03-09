import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from scipy.special import comb

# --- Початкові параметри ---
t_default = 1000 
sigma_default = 920 
lambda0_default = 0.0001
a1_default = 10

def p_1R_vec(x1, t_arr, a1, l0, s1):
    """Векторизована ймовірність P_1R"""
    p = np.exp(-(t_arr**2) / (2 * s1**2))
    return comb(a1, x1) * np.exp(-l0 * t_arr) * (p**x1) * ((1 - p)**(a1 - x1))

def a_1R_vec(k, t_arr, a1, l0, s1):
    """Векторизована щільність відмов a_1R"""
    p = np.exp(-(t_arr**2) / (2 * s1**2))
    el0 = np.exp(-l0 * t_arr)
    total = np.zeros_like(t_arr)
    for x1 in range(int(k), int(a1) + 1):
        term_p = (p**x1) * ((1 - p)**(a1 - x1))
        term_val = term_p * l0 + (x1 * term_p) * (t_arr / s1**2)
        if x1 < a1:
            term_val -= (a1 - x1) * (p**(x1+1)) * ((1 - p)**(a1 - x1 - 1)) * (t_arr / s1**2)
        total += comb(a1, x1) * term_val
    return el0 * total

# --- Логіка інтерактивної візуалізації ---
def create_interactive_plot():
    # Налаштування шрифтів для коректного відображення кирилиці (якщо потрібно)
    plt.rcParams['font.family'] = 'DejaVu Sans' 
    
    t_vals = np.linspace(0, 5000, 500)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(bottom=0.25, hspace=0.4)

    # Початкові графіки
    line1, = ax1.plot(t_vals, p_1R_vec(5, t_vals, a1_default, lambda0_default, sigma_default), lw=2, color='blue')
    line2, = ax2.plot(t_vals, a_1R_vec(5, t_vals, a1_default, lambda0_default, sigma_default), lw=2, color='red')

    ax1.set_title(r"Розподіл ймовірностей $P_{1R}(x_1, t)$")
    ax1.set_ylabel("Ймовірність")
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.set_title(r"Функція щільності відмов $a_{1R}(k, t)$")
    ax2.set_ylabel("Щільність")
    ax2.set_xlabel("Час (t), год")
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Слайдери
    ax_a1 = plt.axes([0.2, 0.15, 0.65, 0.03])
    ax_s1 = plt.axes([0.2, 0.11, 0.65, 0.03])
    ax_l0 = plt.axes([0.2, 0.07, 0.65, 0.03])
    ax_k = plt.axes([0.2, 0.03, 0.65, 0.03])

    s_a1 = Slider(ax_a1, 'К-сть елементів ($a_1$)', 1, 50, valinit=a1_default, valstep=1)
    s_s1 = Slider(ax_s1, 'Параметр $\sigma_1$', 100, 2000, valinit=sigma_default)
    s_l0 = Slider(ax_l0, 'Зовн. відмова $\lambda_0$', 0.00001, 0.001, valinit=lambda0_default, valfmt='%.5f')
    s_k = Slider(ax_k, 'Поріг / Стан ($k, x_1$)', 0, a1_default, valinit=5, valstep=1)

    def update(val):
        a1 = s_a1.val
        s1 = s_s1.val
        l0 = s_l0.val
        k = s_k.val
        
        # Перевірка, щоб k не перевищувало a1
        if k > a1:
            k = a1
            s_k.set_val(a1)
            
        line1.set_ydata(p_1R_vec(k, t_vals, a1, l0, s1))
        line2.set_ydata(a_1R_vec(k, t_vals, a1, l0, s1))
        
        # Автоматичне масштабування осей під нові дані
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()
        fig.canvas.draw_idle()

    s_a1.on_changed(update)
    s_s1.on_changed(update)
    s_l0.on_changed(update)
    s_k.on_changed(update)

    plt.show()

if __name__ == "__main__":
    create_interactive_plot()