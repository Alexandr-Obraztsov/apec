import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
from sympy import simplify

def rep(input, eq):
    for key, value in eq.items():
        input = input.replace(key, value)
    return input

def megaplot(begins, IL, UC):
    def ddt(t, y, eq):
        dydt = eval(eq)
        return dydt
    

    str_eval = "["
    t_span = [0, 1]
    ans = {}; yeq = {}
    for i in IL:
        left_part = i[:i.find("'")+1]
        right_part = i[i.find("=")+2:]
        ans[left_part] = str(simplify(right_part))
    for i in UC:
        left_part = i[:i.find("'")+1]
        right_part = i[i.find("=")+2:]
        ans[left_part] = str(simplify(right_part))
    for i in range(len(begins.keys())):
        yeq[list(begins.keys())[i]] = f"y[{i}]"
    for key, value in ans.items():
        ans[key] = rep(value, yeq)
        str_eval += f"{ans[key]}, "
    str_eval += "]"
    sol = solve_ivp(lambda t, y: ddt(t, y, str_eval), t_span, list(begins.values()))
    for i in range(len(begins.keys())):
        plt.plot(sol.t, sol.y[i], label=f'{list(begins.keys())[i]}')
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
        

