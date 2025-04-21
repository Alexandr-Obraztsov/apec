import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from sympy import simplify

def substitute_variables_in_expression(expression: str, variable_mapping: dict) -> str:
    """
    Заменяет переменные в выражении согласно переданной карте.

    Аргументы:
        expression (str): Строка выражения, в котором требуется замена.
        variable_mapping (dict): Словарь соответствия переменных (ключ — исходная переменная, значение — новая).

    Возвращает:
        str: Новое выражение с заменёнными переменными.
    """
    for key, value in variable_mapping.items():
        expression = expression.replace(key, value)
    return expression

def plot_ode_system_solution(initial_conditions_dict: dict, inductor_equations: list, capacitor_equations: list) -> None:
    """
    Строит график решения системы ОДУ по заданным уравнениям и начальным условиям.

    Аргументы:
        initial_conditions_dict (dict): Начальные условия для переменных (ключ — имя переменной, значение — значение).
        inductor_equations (list): Список уравнений для индуктивностей.
        capacitor_equations (list): Список уравнений для конденсаторов.

    Возвращает:
        None
    """
    def ode_rhs(time, y, ode_equation):
        dydt = eval(ode_equation)
        return dydt
    str_eval = "["
    time_span = [0, 1]
    equations = {}
    y_map = {}
    for eq in inductor_equations:
        left_part = eq[:eq.find("'")+1]
        right_part = eq[eq.find("=")+2:]
        equations[left_part] = str(simplify(right_part))
    for eq in capacitor_equations:
        left_part = eq[:eq.find("'")+1]
        right_part = eq[eq.find("=")+2:]
        equations[left_part] = str(simplify(right_part))
    for i, key in enumerate(initial_conditions_dict.keys()):
        y_map[key] = f"y[{i}]"
    for key, value in equations.items():
        equations[key] = substitute_variables_in_expression(value, y_map)
        str_eval += f"{equations[key]}, "
    str_eval += "]"
    solution = solve_ivp(lambda time, y: ode_rhs(time, y, str_eval), time_span, list(initial_conditions_dict.values()))
    for i, key in enumerate(initial_conditions_dict.keys()):
        plt.plot(solution.t, solution.y[i], label=f'{key}')
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
        

