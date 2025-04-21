import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp

# Модифицируем функцию ode_func для возможности передачи уравнения дифференциального уравнения как аргумента
def ode_func(t, y, eq):
    dydt = eval(eq) # Используем метод eval() для вычисления значения строки как кода Python
    return dydt

# Определяем строку с системой дифференциальных уравнений
eq = "[2*y[0] - 5*y[1] + 3, 5*y[0] - 6*y[1] + 1]"

# Решаем систему дифференциальных уравнений на интервале [0, 10]
t_span = [0, 10]
y0 = [6, 5] # Начальные условия
sol = solve_ivp(lambda t, y: ode_func(t, y, eq), t_span, y0)

# Выводим график решения системы дифференциальных уравнений
plt.plot(sol.t, sol.y[0], label='y1(t)')
plt.plot(sol.t, sol.y[1], label='y2(t)')
plt.xlabel('Time')
plt.ylabel('Values')
plt.title('Solution of system of ODEs')
plt.legend()
plt.show()
