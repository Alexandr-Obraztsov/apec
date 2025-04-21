import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
import networkx as nx
from Line import Line as LineCircuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from collections import defaultdict, OrderedDict, deque
import numpy as np
from functions import get_List_LC, get_elem_nodes, get_connections
from itertools import combinations
from scipy.integrate import odeint
from sympy import *
import matplotlib.pyplot as plt
from give_f import *
from ploti import megaplot


def find_branch_points(graph):
    """
    Функция находит вершины в графе graph, из которых выходит более 2 ребер.
    Возвращает список найденных вершин.
    """
    branch_points = []
    for node in graph.keys():
        if len(graph[node]) > 2:
            branch_points.append(node)
    if branch_points == []:
        return 0
    else:
        return branch_points

def get_one_path(graphin):
    # Создадим пустой список для хранения пути
    path = [0]
    graph = defaultdict(set)
    for key, values in graphin.items():
        graph[int(key)] = {int(value) for value in values}      
    # Итеративно пройдем по всем соседним вершинам, пока не достигнем конца пути
    while len(path) < len(graph):
        neighbors = graph[path[-1]]
        next_node = next(iter(neighbors - set(path)), None)
        if next_node is None:
            raise ValueError("Граф не связный")
        path.append(next_node)
    for i in range(len(path)):
        path[i] = str(path[i])
    return path

def check_for_begin(lc_list, voltages):
    ans = {}
    for i in ((lc_list)):
        if "C" in i:
            ans[f"U_{i}"] = float(input(f"Введите значение {i} до коммутации: "))
        else:
            ans[f"I_{i}"] = float(input(f"Введите значение {i} до коммутации: "))
    return ans

def find_all_paths(graph, start, end, path=None):
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in graph:
        return []
    paths = []
    for node in graph[start]:
        if node not in path:
            new_paths = find_all_paths(graph, node, end, path)
            for new_path in new_paths:
                if end in new_path:
                    paths.append(new_path)
    return paths

def give_names_branches(branches, nodes_list):
    ans = {}
    for elem in branches:
        for i in range(len(elem)-1):
            pos1 = elem[i]; pos2 = elem[i+1]
            x = ""
            for key, value in nodes_list.items():
                if sorted(value[0]+value[1]) == sorted(pos1+pos2):
                    if "X" in key:
                        break
                    elif "R" in key or "V" in key:
                        x = f"I_{key}"
                        break
                    elif "C" in key or "L" in key:
                        x = f"I_{key}"
                        if elem in ans.values():
                            ans = {x if v == elem else k: v for k, v in ans.items()}
                        else:
                            ans[x] = elem
                        break
            if elem not in ans.values():
                ans[x] = elem
            else:
                continue
    return ans
            
def current(nodes_list, connection_list):
    branches = []
    nodes = find_branch_points(connection_list)
    if nodes == 0:
        #for 1 branch
        branches.append(get_one_path(connection_list)+['0'])
        branches = give_names_branches(branches, nodes_list)
    else:
        node_combinations = list(combinations(nodes, 2))
        node_combinations = [comb for comb in node_combinations if (comb[1], comb[0]) not in node_combinations]
        for i in node_combinations:
            branches+= find_all_paths(connection_list, i[0], i[1])
        branches = give_names_branches(branches, nodes_list)
    return branches
        
def voltage(currents, nodes_list):
    ans = {}
    for key, value in nodes_list.items():
        if "X" in key:
            continue
        x = [value[0], value[1]]
        if "V" in key:
            for val in currents.values():
                if any(x == val[::-1][i:i+len(x)] for i in range(len(val[::-1]) - len(x) + 1)):
                    ans[f"U_{key}"] = x
                    break
                elif any(x == val[i:i+len(x)] for i in range(len(val) - len(x) + 1)):
                    ans[f"-U_{key}"] = x
                    break
                else:
                    pass
        else:
            # Для всего кроме E
            for val in currents.values():
                if any(x == val[i:i+len(x)] for i in range(len(val) - len(x) + 1)):
                    ans[f"U_{key}"] = x
                    break
                elif any(x == val[::-1][i:i+len(x)] for i in range(len(val[::-1]) - len(x) + 1)):
                    ans[f"-U_{key}"] = x
                    break
                else:
                    pass
    return ans

def give_numbers(formula, nodes):
    formula = str(formula)
    for key, val in nodes.items():
        if "X" in key:
            continue
        elif "V" in key and key in str(formula):
            formula = formula.replace(f"U_{key}", str(val[2]))
        else:
            if key in formula:
                formula = formula.replace(key, str(val[2]))
                formula = formula.replace(f"_{val[2]}", f"_{key}")
    return formula

def get_formula(currents, voltages, need_to_find, nodes_list, state_variables):
    #creating elements var
    can_be = []
    cant_be= []
    for key in nodes_list:
        if "X" in key:
            continue
        elif "V" in key:
            can_be.append(f"U_{key}")
            # stri = f"U_{key} = Symbol('U_{key}')"
            # exec(stri)
        elif "C" in key:
            can_be.append(key)
            can_be.append(f"U_{key}")            
            # stri = f"{key} = Symbol('{key}')"
            # exec(stri)
            # stri = f"U_{key} = Symbol('U_{key}')"
            # exec(stri)
        elif "L" in key:
            can_be.append(key)
            # stri = f"{key} = Symbol('{key}')"
            # exec(stri)
            # stri = f"U_{key} = Symbol('U_{key}')"
            # exec(stri)
            cant_be.append(f"U_{key}")
        else:
            can_be.append(key)
            # stri = f"{key} = Symbol('{key}')"
            # exec(stri)
            # stri = f"U_{key} = Symbol('U_{key}')"
            # exec(stri)
            cant_be.append(f"U_{key}")
    for key in currents:
        # stri = f"{key} = Symbol('{key}')"
        # exec(stri)
        if "I_L" in key:
            can_be.append(f"{key}")            
        if "I_C" in key or "I_R" in key or "I_V" in key:
            cant_be.append(key)
    
    del key
    I_set, U_set = get_formul(can_be=can_be, cant_be=cant_be, need_to_find=need_to_find, 
               currents=currents, 
               voltages=voltages, nodes_list=nodes_list, 
               connections=connection_list)
    IL = []; UC = []
    for key, value in I_set.items():
        I_set[key] = simplify(give_numbers(value, nodes_list))
        UC.append(give_numbers(f"U_{key[2:]}' = ({I_set[key]})/{key[2:]}", nodes_list))
    for key, value in U_set.items():
        U_set[key] = simplify(give_numbers(value, nodes_list))  
        IL.append(give_numbers(f"I_{key[2:]}' = ({U_set[key]})/{key[2:]}", nodes_list))
    begins = check_for_begin(lc_list, voltages)
    megaplot(begins, IL, UC)

if __name__ == "__main__":
    """
    СХЕМА ДОЖНА БЫТЬ ТАКАЯ, ЧТОБЫ ИЗ 1 УЗЛА МОЖНО БЫЛО ПОПАСТЬ ВО ВСЕ ОСТАЛЬНЫЕ(ЕСЛИ УЗЛЫ ЕСТЬ)
    НИКАКИХ ПАРАЛЛЕЛЬНЫХ РЕЗИСТОРОВ, НО МОЖНО В КОМБИНАЦИИ С ДРУГИМИ ЭЛЕМЕНТАМИ
    
    """
    circuit = Circuit('1')
    # Posl C
    # circuit.V(1, 1, circuit.gnd, 100@u_V)
    # circuit.C(1, 2, circuit.gnd, 0.001@u_F)
    # circuit.R(1, 1, 2, 1@u_Ω)
    #Posl L
    # circuit.V(1, 1, circuit.gnd, 100@u_V)
    # circuit.L(1, 2, circuit.gnd, 0.001@u_H)
    # circuit.R(1, 1, 2, 1@u_Ω)
    #Paral RLC
    circuit.subcircuit(LineCircuit('Line'))
    circuit.V(1, 1, circuit.gnd, 100@u_V)
    circuit.R(1, 1, 2, 1@u_Ω)
    circuit.L(1, 2, 3, 0.001@u_H)
    circuit.R(3, 3, 5, 10@u_Ohm)
    circuit.C(1, 5, circuit.gnd, 0.001@u_F)
    circuit.X(1, 'Line', 3, 4)
    circuit.R(2, 4, circuit.gnd, 2@u_Ohm)
    

    lc_list = get_List_LC(circuit)
    nodes_list = get_elem_nodes(circuit)
    connection_list = get_connections(circuit)
    print(connection_list)
    simulator = circuit.simulator(temperature=25, nominal_temperature =25)
    analysis = simulator.operating_point()
    need_to_find = [[], []]
    state_Variables = []
    for i in lc_list:
        if "L" in i:
            need_to_find[0].append(f"U_{str(i)}")
            state_Variables.append(f"I_{str(i)}")
        else:
            need_to_find[1].append(f"I_{str(i)}")
            state_Variables.append(f"U_{str(i)}")
    #Нужно сделать так чтобы опр нормальные ветви
    currents = current(nodes_list, connection_list)
    voltages = voltage(currents, nodes_list)
    print(currents)
    print(voltages)
    get_formula(currents, voltages, need_to_find, nodes_list, state_Variables)