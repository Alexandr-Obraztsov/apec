import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
import networkx as nx
from utilits.transmission_line import TransmissionLine as LineCircuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

from collections import defaultdict, OrderedDict, deque
import numpy as np
from utilits.circuit_tools import get_inductors_and_capacitors, get_element_nodes_dict, get_node_connections, find_junction_nodes, find_single_path, find_all_paths_between_nodes, assign_branch_names, calculate_branches, substitute_element_values
from itertools import combinations
from scipy.integrate import odeint
from sympy import *
import matplotlib.pyplot as plt
from utilits.equation_generator import generate_circuit_equations
from utilits.plotting import plot_ode_system_solution


def input_initial_conditions(lc_elements: list, voltages: dict) -> dict:
    """
    Запрашивает у пользователя начальные условия для элементов схемы.

    Аргументы:
        lc_elements (list): Список имён индуктивностей и конденсаторов.
        voltages (dict): Словарь напряжений на элементах.

    Возвращает:
        dict: Словарь с начальными условиями для каждого элемента.
    """
    initial_conditions = {}
    for element in lc_elements:
        if "C" in element:
            initial_conditions[f"U_{element}"] = float(input(f"Введите значение {element} до коммутации: "))
        else:
            initial_conditions[f"I_{element}"] = float(input(f"Введите значение {element} до коммутации: "))
    return initial_conditions


def calculate_voltages(currents: dict, nodes_list: dict) -> dict:
    """
    Вычисляет напряжения на элементах схемы по токам и списку узлов.

    Аргументы:
        currents (dict): Словарь токов в ветвях.
        nodes_list (dict): Словарь с информацией об узлах элементов.

    Возвращает:
        dict: Словарь напряжений на элементах.
    """
    voltages = {}
    for key, value in nodes_list.items():
        if "X" in key:
            continue
        node_pair = [value[0], value[1]]
        if "V" in key:
            for branch in currents.values():
                if any(node_pair == branch[::-1][i:i+len(node_pair)] for i in range(len(branch[::-1]) - len(node_pair) + 1)):
                    voltages[f"U_{key}"] = node_pair
                    break
                elif any(node_pair == branch[i:i+len(node_pair)] for i in range(len(branch) - len(node_pair) + 1)):
                    voltages[f"-U_{key}"] = node_pair
                    break
        else:
            for branch in currents.values():
                if any(node_pair == branch[i:i+len(node_pair)] for i in range(len(branch) - len(node_pair) + 1)):
                    voltages[f"U_{key}"] = node_pair
                    break
                elif any(node_pair == branch[::-1][i:i+len(node_pair)] for i in range(len(branch[::-1]) - len(node_pair) + 1)):
                    voltages[f"-U_{key}"] = node_pair
                    break
    return voltages


def generate_equations_for_circuit(currents: dict, voltages: dict, need_to_find: list, nodes_list: dict, state_variables: list) -> None:
    """
    Генерирует уравнения для моделирования электрической схемы и строит график решения.

    Аргументы:
        currents (dict): Словарь токов в ветвях.
        voltages (dict): Словарь напряжений на элементах.
        need_to_find (list): Список переменных, которые нужно найти.
        nodes_list (dict): Словарь с информацией об узлах элементов.
        state_variables (list): Список переменных состояния.

    Возвращает:
        None
    """
    can_be = []
    cant_be = []
    for key in nodes_list:
        if "X" in key:
            continue
        elif "V" in key:
            can_be.append(f"U_{key}")
        elif "C" in key:
            can_be.append(key)
            can_be.append(f"U_{key}")
        elif "L" in key:
            can_be.append(key)
            cant_be.append(f"U_{key}")
        else:
            can_be.append(key)
            cant_be.append(f"U_{key}")
    for key in currents:
        if "I_L" in key:
            can_be.append(f"{key}")
        if "I_C" in key or "I_R" in key or "I_V" in key:
            cant_be.append(key)
    del key
    i_set, u_set = generate_circuit_equations(can_be=can_be, cant_be=cant_be, need_to_find=need_to_find,
                                         branch_current_map=currents,
                                         voltage_map=voltages, element_nodes=nodes_list,
                                         element_graph=connection_list)
    il_equations = []
    uc_equations = []
    for key, value in i_set.items():
        i_set[key] = simplify(substitute_element_values(value, nodes_list))
        uc_equations.append(substitute_element_values(f"U_{key[2:]}' = ({i_set[key]})/{key[2:]}", nodes_list))
    for key, value in u_set.items():
        u_set[key] = simplify(substitute_element_values(value, nodes_list))
        il_equations.append(substitute_element_values(f"I_{key[2:]}' = ({u_set[key]})/{key[2:]}", nodes_list))
    initial_conditions_dict = input_initial_conditions(lc_list, voltages)
    plot_ode_system_solution(initial_conditions_dict, il_equations, uc_equations)


if __name__ == "__main__":
    """
    СХЕМА ДОЖНА БЫТЬ ТАКАЯ, ЧТОБЫ ИЗ 1 УЗЛА МОЖНО БЫЛО ПОПАСТЬ ВО ВСЕ ОСТАЛЬНЫЕ(ЕСЛИ УЗЛЫ ЕСТЬ)
    НИКАКИХ ПАРАЛЛЕЛЬНЫХ РЕЗИСТОРОВ, НО МОЖНО В КОМБИНАЦИИ С ДРУГИМИ ЭЛЕМЕНТАМИ
    """
    circuit = Circuit('1')
    # Примеры схем:
    # circuit.V(1, 1, circuit.gnd, 100@u_V)
    # circuit.C(1, 2, circuit.gnd, 0.001@u_F)
    # circuit.R(1, 1, 2, 1@u_Ω)
    # circuit.L(1, 2, circuit.gnd, 0.001@u_H)
    # circuit.R(1, 1, 2, 1@u_Ω)
    circuit.subcircuit(LineCircuit('Line'))
    circuit.V(1, 1, circuit.gnd, 100@u_V)
    circuit.R(1, 1, 2, 1@u_Ω)
    circuit.L(1, 2, 3, 0.001@u_H)
    circuit.R(3, 3, 5, 10@u_Ohm)
    circuit.C(1, 5, circuit.gnd, 0.001@u_F)
    circuit.X(1, 'Line', 3, 4)
    circuit.R(2, 4, circuit.gnd, 2@u_Ohm)

    lc_list = get_inductors_and_capacitors(circuit)
    nodes_list = get_element_nodes_dict(circuit)
    connection_list = get_node_connections(circuit)
    print(connection_list)
    simulator = circuit.simulator(temperature=25, nominal_temperature=25)
    analysis = simulator.operating_point()
    need_to_find = [[], []]
    state_variables = []
    for element in lc_list:
        if "L" in element:
            need_to_find[0].append(f"U_{str(element)}")
            state_variables.append(f"I_{str(element)}")
        else:
            need_to_find[1].append(f"I_{str(element)}")
            state_variables.append(f"U_{str(element)}")
    currents = calculate_branches(nodes_list, connection_list)
    voltages = calculate_voltages(currents, nodes_list)
    print(currents)
    print(voltages)
    generate_equations_for_circuit(currents, voltages, need_to_find, nodes_list, state_variables)