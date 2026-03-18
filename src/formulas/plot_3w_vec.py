# src/formulas/plot_3w_vec.py
import numpy as np
from scipy.special import comb

_EPS = 1e-9


def _stabilize_q_curve(q_vals: np.ndarray) -> np.ndarray:
    """
    Prepare Q(t) for derivative/hazard computations:
    - keep values in [0, 1)
    - enforce monotone non-decreasing behavior expected for failure probability
    """
    q = np.asarray(q_vals, dtype=float)
    q = np.clip(q, 0.0, 1.0 - _EPS)
    return np.maximum.accumulate(q)


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
    
    return _stabilize_q_curve(1 - sum_p3)

def a_3w_vec(t, q_vals):
    """ Щільність відмов a_3W(t) через чисельне диференціювання """
    q = _stabilize_q_curve(q_vals)
    density = np.gradient(q, t, edge_order=2)
    return np.clip(density, 0.0, None)

def lambda_3w_vec(t, a_vals, q_vals):
    """ Інтенсивність відмов lambda_3W(t) = a(t) / P(t) """
    q = _stabilize_q_curve(q_vals)
    p_vals = np.clip(1.0 - q, _EPS, None)
    a_nonnegative = np.clip(np.asarray(a_vals, dtype=float), 0.0, None)
    hazard = a_nonnegative / p_vals
    return np.nan_to_num(hazard, nan=0.0, posinf=0.0, neginf=0.0)