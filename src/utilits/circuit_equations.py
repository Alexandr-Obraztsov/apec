from scipy import *
from sympy import *

def is_sublist_in_list(lst, sub_lst):
    for i in range(len(lst) - len(sub_lst) + 1):
        if lst[i:i+len(sub_lst)] == sub_lst:
            return True
    return False

def normalize_operators(expr):
    # Избавление от --, ++, +- и -+
    return expr.replace('--', '+').replace('++', '+').replace('+-', '-').replace('-+', '-')

def find_all_graph_paths(graph, start, end, path=None):
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
            new_paths = find_all_graph_paths(graph, node, end, path)
            for new_path in new_paths:
                if end in new_path:
                    paths.append(new_path)
    return paths

def kirchhoff_current_eq(branch_name, branch_currents):
    equation = ""
    for key, value in branch_currents.items():
        if branch_name == key:
            continue
        elif branch_currents[branch_name][0] == value[0]:
            equation += f"-{key}"
        elif branch_currents[branch_name][0] == value[len(value)-1]:
            equation += f"+{key}"
    return Eq(simplify(f"{branch_name}"), simplify(equation))

def find_forbidden_currents(forbidden_list, formula):
    forbidden = []
    for item in forbidden_list:
        if formula.has(simplify(item)):
            forbidden.append(item)
    return forbidden

def get_element_terminal_nodes(element_name, graph):
    pos1 = graph[element_name][0]
    pos2 = graph[element_name][len(graph[element_name])-1]
    return [pos1, pos2]

def get_resistors_from_path(path, nodes):
    resistors = []
    for i in range(len(path)-1):
        pos1 = path[i]
        pos2 = path[i+1]
        for key, value in nodes.items():
            if ((pos1 == value[0] and pos2 == value[1]) or (pos1 == value[1] and pos2 == value[0])) and "R" in key:
                resistors.append(key)
    return "+".join(resistors)

def filter_valid_paths(paths, nodes):
    valid = {}
    for key, value in nodes.items():
        if "X" in key or "V" in key or "R" in key:
            continue
        valid[key] = (value[:2])
    result = {}
    for key, node_pair in valid.items():
        for path in paths:
            if is_sublist_in_list(path, node_pair) or path == node_pair or path[::-1] == node_pair or is_sublist_in_list(path, node_pair[::-1]):
                result[key] = path
                break
    return result

def voltage_expr_along_path(paths, voltages, name):
    element = name[name.find('_')+1:]
    xpath = paths[element]
    expr = []
    for i in range(len(xpath)-1):
        pos1 = xpath[i]
        pos2 = xpath[i+1]
        for key, value in voltages.items():
            if [pos1, pos2] == value:
                expr.append(key)
            elif [pos1, pos2] == value[::-1]:
                expr.append(f"-{key}")
    expr = "+".join(expr)
    expr = normalize_operators(expr)
    return expr

def find_forbidden_voltages(forbidden_list, formula):
    forbidden = []
    for item in forbidden_list:
        if item in formula:
            forbidden.append(item)
    return forbidden

def find_current_by_nodes(branch_currents, node_pair):
    for key, value in branch_currents.items():
        if all(elem in value for elem in node_pair):
            return key

def voltage_to_ohm_law(voltage_list, voltages, branch_currents):
    result = {}
    for voltage in voltage_list:
        if voltage in voltages:
            node_pair = voltages[voltage]
        elif f"-{voltage}" in voltages:
            node_pair = voltages[f"-{voltage}"][::-1]
        resistance = voltage[voltage.find("_")+1:]
        current = find_current_by_nodes(branch_currents, node_pair)
        result[voltage] = f"({current}*{resistance})"
    return result

def solve_forbidden_currents(forbidden_list, branch_currents, voltages, nodes_list, connections, name, cant_be):
    result = {}
    for elem in forbidden_list:
        node_pair = get_element_terminal_nodes(elem, branch_currents)
        resistance = "(" + get_resistors_from_path(branch_currents[elem], nodes_list) + ")"
        paths = find_all_graph_paths(connections, node_pair[0], node_pair[1])
        paths = filter_valid_paths(paths, nodes_list)
        expr = voltage_expr_along_path(paths, voltages, name)
        forbidden = find_forbidden_voltages(cant_be, expr)
        if not forbidden:
            result[elem] = f"({expr})/{resistance}"
            continue
        else:
            formula = voltage_to_ohm_law(forbidden, voltages, branch_currents)
            for key, value in formula.items():
                expr = expr.replace(key, value)
        result[elem] = f"({expr})/{resistance}"
    return result

def get_circuit_equations(can_be, cant_be, need_to_find, branch_currents,
                voltages, nodes_list, connections):
    u_set = {}
    i_set = {}
    i_max_set = []
    for elem in need_to_find[1]:
        if len(branch_currents) == 1:
            def get_u_from_path(path, voltages):
                expr = []
                for i in range(0, len(path)-1):
                    pos1 = path[i]
                    pos2 = path[i+1]
                    for key, val in voltages.items():
                        if "R" in key or "X" in key:
                            continue
                        elif [pos1, pos2] == val:
                            if "V" in key:
                                expr.append(f"-{key}")
                                break
                            expr.append(f"-{key}")
                            break
                        elif [pos2, pos1] == val:
                            if "V" in key:
                                expr.append(f"+{key}")
                                break
                            expr.append(f"+{key}")
                            break
                expr = "+".join(expr)
                expr = normalize_operators(expr)
                return expr
            resistance = get_resistors_from_path(branch_currents[elem], nodes_list)
            voltage = get_u_from_path(branch_currents[elem], voltages)
            i_set[elem] = simplify(f"({voltage})/({resistance})")
        else:
            equation = kirchhoff_current_eq(elem, branch_currents)
            forbidden = find_forbidden_currents(cant_be, equation.rhs)
            if not forbidden:
                i_set[elem] = equation
                break
            else:
                solved = solve_forbidden_currents(forbidden, branch_currents, voltages, nodes_list, connections, elem, cant_be)
                i_eq = []
                for key, value in solved.items():
                    i_eq.append(Eq(simplify(key), simplify(value)))
                for eq in i_eq:
                    equation = equation.subs(eq.lhs, eq.rhs)
                    i_set[elem] = solve(equation, equation.lhs)[0]
                i_max_set.append(equation)
                for eq in i_eq:
                    i_max_set.append(eq)
    for elem in need_to_find[0]:
        def get_u_from_path(path, voltages):
            expr = []
            for i in range(0, len(path)-1):
                pos1 = path[i]
                pos2 = path[i+1]
                for key, val in voltages.items():
                    if "X" in key:
                        continue
                    elif [pos1, pos2] == val:
                        expr.append(f"+{key}")
                        break
                    elif [pos2, pos1] == val:
                        expr.append(f"-{key}")
                        break
            expr = "+".join(expr)
            expr = normalize_operators(expr)
            return expr
        if len(branch_currents) == 1:
            if elem in voltages.keys():
                node_pair = voltages[elem]
            else:
                node_pair = voltages[elem][::-1]
            path = find_all_graph_paths(connections, node_pair[0], node_pair[1])
            path.remove(node_pair)
            formula = get_u_from_path(path[0], voltages)
            forbidden = find_forbidden_voltages(cant_be, formula)
            x = voltage_to_ohm_law(forbidden, voltages, branch_currents)
            for key, value in x.items():
                formula = formula.replace(key, value)
            u_set[elem] = simplify(formula)
        else:
            node_pair = voltages[elem]
            paths = find_all_graph_paths(connections, node_pair[0], node_pair[1])
            paths.remove(node_pair)
            paths = filter_valid_paths(paths, nodes_list)
            formulas = []
            for key, path in paths.items():
                formulas.append(get_u_from_path(path, voltages))
            is_good_formula = False
            while True:
                if is_good_formula:
                    break
                forbidden = find_forbidden_voltages(cant_be, formulas[0])
                u_eq = voltage_to_ohm_law(forbidden, voltages, branch_currents)
                for key, value in u_eq.items():
                    formulas[0] = formulas[0].replace(key, f"{value}")
                for key, value in i_set.items():
                    if key in formulas[0]:
                        formulas[0] = formulas[0].replace(key, f"{value}")
                if find_forbidden_currents(cant_be, simplify(formulas[0])) == []:
                    is_good_formula = True
            u_set[elem] = simplify(formulas[0])
    print(i_set, u_set, sep='\n')
    return i_set, u_set