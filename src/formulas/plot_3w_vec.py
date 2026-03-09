# src/formulas/plot_3w_vec.py
import numpy as np
from scipy.special import comb

def q_3w_vec(t, a1, k1, l1, b1, a2, k2, l2, b2, a3, k3, l3, b3, l0):
    """ Розрахунок ймовірності відмови Q_3W(t) для 3 рівнів """
    # Level 1
    p1 = np.exp(-l1 * (t ** b1))
    sum_p1 = np.zeros_like(t)
    for x1 in range(int(k1), int(a1) + 1):
        sum_p1 += comb(a1, x1) * (p1**x1) * ((1 - p1)**(a1 - x1))
    sum_p1 *= np.exp(-l0 * t) 
    
    # Level 2
    p2 = np.exp(-l2 * (t ** b2))
    sum_p2 = np.zeros_like(t)
    for x2 in range(int(k2), int(a2) + 1):
        sum_p2 += comb(a2, x2) * (p2**x2) * ((1 - p2)**(a2 - x2))
    sum_p2 *= sum_p1
    
    # Level 3
    p3 = np.exp(-l3 * (t ** b3))
    sum_p3 = np.zeros_like(t)
    for x3 in range(int(k3), int(a3) + 1):
        sum_p3 += comb(a3, x3) * (p3**x3) * ((1 - p3)**(a3 - x3))
    sum_p3 *= sum_p2
    
    return 1 - sum_p3

def a_3w_vec(t, q_vals):
    """ Щільність відмов a_3W(t) через чисельне диференціювання """
    return np.gradient(q_vals, t)

def lambda_3w_vec(t, a_vals, q_vals):
    """ Інтенсивність відмов lambda_3W(t) = a(t) / P(t) """
    p_vals = 1 - q_vals
    # Prevent division by zero if P(t) hits 0 at extreme times
    p_vals = np.where(p_vals == 0, 1e-10, p_vals)
    return a_vals / p_vals