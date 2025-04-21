import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

# Модифицируем функцию ode_system_rhs для возможности передачи уравнения дифференциального уравнения как аргумента
def ode_system_rhs(time: float, state_vector: list, ode_equations: str) -> list:
    """
    Правая часть системы ОДУ, вычисляет производные по заданному уравнению.

    Аргументы:
        time (float): Текущее время.
        state_vector (list): Вектор состояния (значения переменных).
        ode_equations (str): Строка с системой дифференциальных уравнений.

    Возвращает:
        list: Список производных (правые части системы ОДУ).
    """
    derivatives = eval(ode_equations)
    return derivatives

# Определяем строку с системой дифференциальных уравнений
ode_equations = "[2*state_vector[0] - 5*state_vector[1] + 3, 5*state_vector[0] - 6*state_vector[1] + 1]"

# Решаем систему дифференциальных уравнений на интервале [0, 10]
time_span = [0, 10]
initial_state = [6, 5] # Начальные условия
solution = solve_ivp(lambda time, state_vector: ode_system_rhs(time, state_vector, ode_equations), time_span, initial_state)

# Выводим график решения системы дифференциальных уравнений
plt.plot(solution.t, solution.y[0], label='y1(t)')
plt.plot(solution.t, solution.y[1], label='y2(t)')
plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Solution of system of ODEs')
plt.legend()
plt.show()
