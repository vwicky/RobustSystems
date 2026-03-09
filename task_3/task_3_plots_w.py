import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.special import comb

# --- Початкові параметри (За замовчуванням) ---
a1_init = 5
k_init = 4
lambda0_init = 0.0002
lambda1_init = 0.0002
beta1_init = 1.3

# --- Математичні функції (Векторизовані для NumPy) ---

def p_1w_vec(x1, t, a1, l0, l1, b1):
    """Ймовірність перебування в стані x1 (Вейбулл + експонента)"""
    # p - ймовірність безвідмовної роботи одного елемента за Вейбуллом
    p = np.exp(-l1 * (t ** b1))
    
    # Біноміальна складова
    c_nx = comb(a1, x1)
    binom = c_nx * (p**x1) * ((1 - p)**(a1 - x1))
    
    # Складова зовнішньої відмови
    ext_fail = np.exp(-l0 * t)
    
    return ext_fail * binom

def q_1w_vec(k, t, a1, l0, l1, b1):
    """Ймовірність відмови системи Q_1W(k; t) = 1 - сума P_1W від k до a1"""
    reliability = np.zeros_like(t)
    for x in range(int(k), int(a1) + 1):
        reliability += p_1w_vec(x, t, a1, l0, l1, b1)
    return 1 - reliability

def a_1w_vec(k, t, a1, l0, l1, b1):
    """Щільність відмов a_1W(k; t) — оптимізована версія вашої a_1W_verbose"""
    p = np.exp(-l1 * (t ** b1))
    ext_fail = np.exp(-l0 * t)
    
    # Похідна p по t: dp/dt
    dp_dt = -l1 * b1 * (t ** (b1 - 1)) * p
    
    total_density = np.zeros_like(t)
    
    for x1 in range(int(k), int(a1) + 1):
        c_nx = comb(a1, x1)
        # Похідна біноміальної частини (P_1W без e^-l0t)
        # d/dt [p^x * (1-p)^(a-x)] = x*p^(x-1)*(1-p)^(a-x)*dp/dt - (a-x)*p^x*(1-p)^(a-x-1)*dp/dt
        
        term_p = (p**x1) * ((1 - p)**(a1 - x1))
        
        # Вплив зміни стану елементів
        d_binom_dt = np.zeros_like(t)
        if x1 > 0:
            d_binom_dt += x1 * (p**(x1-1)) * ((1-p)**(a1-x1)) * dp_dt
        if x1 < a1:
            d_binom_dt -= (a1-x1) * (p**x1) * ((1-p)**(a1-x1-1)) * dp_dt
            
        # Загальна похідна для стану x1: d/dt [exp(-l0*t) * Binom]
        # = -l0 * exp(-l0*t) * Binom + exp(-l0*t) * d_binom_dt
        state_density = -(-l0 * ext_fail * term_p + ext_fail * d_binom_dt)
        total_density += c_nx * state_density
        
    return total_density

# --- Побудова інтерактивного графіка ---

def create_interactive_plot():
    # Використовуємо шрифт, що підтримує кирилицю
    plt.rcParams['font.family'] = 'DejaVu Sans'
    t_vals = np.linspace(0.1, 5000, 500)
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(bottom=0.35, hspace=0.4)

    # Початкові лінії (використовуємо r'' для LaTeX)
    line1, = ax1.plot(t_vals, q_1w_vec(k_init, t_vals, a1_init, lambda0_init, lambda1_init, beta1_init), 
                      lw=2, color='darkorange')
    line2, = ax2.plot(t_vals, a_1w_vec(k_init, t_vals, a1_init, lambda0_init, lambda1_init, beta1_init), 
                      lw=2, color='forestgreen')

    ax1.set_title(r"Ймовірність відмови системи $Q_{1W}(k; t)$")
    ax1.set_ylabel(r"Ймовірність $Q$")
    ax1.set_ylim(-0.05, 1.05)
    ax1.grid(True, linestyle='--', alpha=0.6)

    ax2.set_title(r"Щільність відмов $a_{1W}(k; t)$")
    ax2.set_ylabel(r"Щільність $a$")
    ax2.set_xlabel("Час (t), год")
    ax2.grid(True, linestyle='--', alpha=0.6)

    # Слайдери (Зверніть увагу на префікс r перед рядками!)
    ax_color = 'lightgoldenrodyellow'
    ax_a1 = plt.axes([0.2, 0.22, 0.65, 0.02], facecolor=ax_color)
    ax_k  = plt.axes([0.2, 0.18, 0.65, 0.02], facecolor=ax_color)
    ax_l1 = plt.axes([0.2, 0.14, 0.65, 0.02], facecolor=ax_color)
    ax_b1 = plt.axes([0.2, 0.10, 0.65, 0.02], facecolor=ax_color)
    ax_l0 = plt.axes([0.2, 0.06, 0.65, 0.02], facecolor=ax_color)

    s_a1 = Slider(ax_a1, r'$a_1$ (елем.)', 1, 30, valinit=a1_init, valstep=1)
    s_k  = Slider(ax_k,  r'$k$ (поріг)', 1, a1_init, valinit=k_init, valstep=1)
    s_l1 = Slider(ax_l1, r'$\lambda_1$', 0.00001, 0.001, valinit=lambda1_init, valfmt='%.5f')
    s_b1 = Slider(ax_b1, r'$\beta_1$ (форма)', 0.5, 3.0, valinit=beta1_init)
    s_l0 = Slider(ax_l0, r'$\lambda_0$ (зовн.)', 0.00001, 0.001, valinit=lambda0_init, valfmt='%.5f')

    def update(val):
        a1 = s_a1.val
        l1 = s_l1.val
        b1 = s_b1.val
        l0 = s_l0.val
        
        # Обмеження порогу k
        current_k = s_k.val
        if current_k > a1:
            s_k.set_val(a1)
            current_k = a1
            
        line1.set_ydata(q_1w_vec(current_k, t_vals, a1, l0, l1, b1))
        line2.set_ydata(a_1w_vec(current_k, t_vals, a1, l0, l1, b1))
        
        ax1.relim()
        ax1.autoscale_view(scalex=False)
        ax2.relim()
        ax2.autoscale_view(scalex=False)
        fig.canvas.draw_idle()

    s_a1.on_changed(update)
    s_k.on_changed(update)
    s_l1.on_changed(update)
    s_b1.on_changed(update)
    s_l0.on_changed(update)

    plt.show()

if __name__ == "__main__":
    create_interactive_plot()