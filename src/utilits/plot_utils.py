import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from sympy import simplify

def substitute_vars_in_expr(expr, var_map):
    for key, value in var_map.items():
        expr = expr.replace(key, value)
    return expr

def plot_ode_solution(initial_conditions, il_equations, uc_equations):
    def ode_rhs(t, y, eq):
        dydt = eval(eq)
        return dydt
    str_eval = "["
    t_span = [0, 1]
    equations = {}
    y_map = {}
    for eq in il_equations:
        left_part = eq[:eq.find("'")+1]
        right_part = eq[eq.find("=")+2:]
        equations[left_part] = str(simplify(right_part))
    for eq in uc_equations:
        left_part = eq[:eq.find("'")+1]
        right_part = eq[eq.find("=")+2:]
        equations[left_part] = str(simplify(right_part))
    for i, key in enumerate(initial_conditions.keys()):
        y_map[key] = f"y[{i}]"
    for key, value in equations.items():
        equations[key] = substitute_vars_in_expr(value, y_map)
        str_eval += f"{equations[key]}, "
    str_eval += "]"
    sol = solve_ivp(lambda t, y: ode_rhs(t, y, str_eval), t_span, list(initial_conditions.values()))
    for i, key in enumerate(initial_conditions.keys()):
        plt.plot(sol.t, sol.y[i], label=f'{key}')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.legend()
    plt.grid()
    plt.show()
    
    # plt.plot(sol.t, sol.y[0], label='y1(t)')
    # plt.plot(sol.t, sol.y[1], label='y2(t)')
    # plt.xlabel('Time')
    # plt.ylabel('Values')
    # plt.title('Solution of system of ODEs')
    # plt.legend()
    # plt.show()
        

