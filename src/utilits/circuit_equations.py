from scipy import *
from sympy import *

def is_sublist(main_list: list, sublist: list) -> bool:
    """
    Проверяет, является ли sublist подсписком main_list.

    Аргументы:
        main_list (list): Основной список.
        sublist (list): Проверяемый подсписок.

    Возвращает:
        bool: True, если sublist является подсписком main_list, иначе False.
    """
    for i in range(len(main_list) - len(sublist) + 1):
        if main_list[i:i+len(sublist)] == sublist:
            return True
    return False

def normalize_operators(expression: str) -> str:
    """
    Нормализует операторы в выражении (заменяет --, ++, +- и -+).

    Аргументы:
        expression (str): Строка выражения.

    Возвращает:
        str: Нормализованное выражение.
    """
    return expression.replace('--', '+').replace('++', '+').replace('+-', '-').replace('-+', '-')

def find_all_paths_in_graph(element_graph: dict, start: str, end: str, path: list = None) -> list:
    """
    Находит все пути между двумя узлами в графе.

    Аргументы:
        element_graph (dict): Словарь, представляющий граф.
        start (str): Начальная вершина.
        end (str): Конечная вершина.
        path (list, optional): Текущий путь (для рекурсии).

    Возвращает:
        list: Список всех возможных путей (каждый путь — список вершин).
    """
    if path is None:
        path = []
    path = path + [start]
    if start == end:
        return [path]
    if start not in element_graph:
        return []
    path_list = []
    for node in element_graph[start]:
        if node not in path:
            new_paths = find_all_paths_in_graph(element_graph, node, end, path)
            for new_path in new_paths:
                if end in new_path:
                    path_list.append(new_path)
    return path_list

def get_kirchhoff_current_equation(branch: str, branch_current_map: dict) -> Eq:
    """
    Составляет уравнение по первому закону Кирхгофа для заданной ветви.

    Аргументы:
        branch (str): Имя ветви.
        branch_current_map (dict): Словарь токов в ветвях.

    Возвращает:
        Eq: Символьное уравнение (sympy Eq) для ветви.
    """
    equation = ""
    for key, value in branch_current_map.items():
        if branch == key:
            continue
        elif branch_current_map[branch][0] == value[0]:
            equation += f"-{key}"
        elif branch_current_map[branch][0] == value[len(value)-1]:
            equation += f"+{key}"
    return Eq(simplify(f"{branch}"), simplify(equation))

def get_forbidden_currents(forbidden_names: list, sympy_formula) -> list:
    """
    Находит запрещённые токи в формуле.

    Аргументы:
        forbidden_names (list): Список имён запрещённых токов.
        sympy_formula: Символьное выражение (sympy).

    Возвращает:
        list: Список запрещённых токов, найденных в формуле.
    """
    forbidden = []
    for item in forbidden_names:
        if sympy_formula.has(simplify(item)):
            forbidden.append(item)
    return forbidden

def get_element_terminals(element: str, element_graph: dict) -> list:
    """
    Возвращает клеммы (узлы) элемента по его имени.

    Аргументы:
        element (str): Имя элемента.
        element_graph (dict): Словарь с информацией о соединениях элементов.

    Возвращает:
        list: Список клемм (узлов) элемента.
    """
    pos1 = element_graph[element][0]
    pos2 = element_graph[element][len(element_graph[element])-1]
    return [pos1, pos2]

def get_resistor_names_from_path(path: list, element_nodes: dict) -> str:
    """
    Возвращает строку с резисторами, встречающимися на пути.

    Аргументы:
        path (list): Список узлов пути.
        element_nodes (dict): Словарь с информацией об узлах элементов.

    Возвращает:
        str: Строка с именами резисторов, разделёнными знаком '+'.
    """
    resistors = []
    for i in range(len(path)-1):
        pos1 = path[i]
        pos2 = path[i+1]
        for key, value in element_nodes.items():
            if ((pos1 == value[0] and pos2 == value[1]) or (pos1 == value[1] and pos2 == value[0])) and "R" in key:
                resistors.append(key)
    return "+".join(resistors)

def filter_valid_element_paths(path_list: list, element_nodes: dict) -> dict:
    """
    Фильтрует пути, оставляя только те, которые соответствуют элементам схемы.

    Аргументы:
        path_list (list): Список всех возможных путей.
        element_nodes (dict): Словарь с информацией об узлах элементов.

    Возвращает:
        dict: Словарь, где ключ — имя элемента, значение — путь (список узлов).
    """
    valid = {}
    for key, value in element_nodes.items():
        if "X" in key or "V" in key or "R" in key:
            continue
        valid[key] = (value[:2])
    result = {}
    for key, node_pair in valid.items():
        for path in path_list:
            if is_sublist(path, node_pair) or path == node_pair or path[::-1] == node_pair or is_sublist(path, node_pair[::-1]):
                result[key] = path
                break
    return result

def get_voltage_expression_along_path(path_dict: dict, voltage_map: dict, element_key: str) -> str:
    """
    Формирует выражение для напряжения вдоль пути.

    Аргументы:
        path_dict (dict): Словарь путей.
        voltage_map (dict): Словарь напряжений.
        element_key (str): Имя элемента.

    Возвращает:
        str: Символьное выражение для напряжения вдоль пути.
    """
    element = element_key[element_key.find('_')+1:]
    xpath = path_dict[element]
    expr = []
    for i in range(len(xpath)-1):
        pos1 = xpath[i]
        pos2 = xpath[i+1]
        for key, value in voltage_map.items():
            if [pos1, pos2] == value:
                expr.append(key)
            elif [pos1, pos2] == value[::-1]:
                expr.append(f"-{key}")
    expr = "+".join(expr)
    expr = normalize_operators(expr)
    return expr

def get_forbidden_voltages(forbidden_names: list, expression: str) -> list:
    """
    Находит запрещённые напряжения в формуле.

    Аргументы:
        forbidden_names (list): Список имён запрещённых напряжений.
        expression (str): Строка выражения.

    Возвращает:
        list: Список запрещённых напряжений, найденных в выражении.
    """
    forbidden = []
    for item in forbidden_names:
        if item in expression:
            forbidden.append(item)
    return forbidden

def get_current_by_nodes(branch_current_map: dict, node_pair_list: list) -> str:
    """
    Находит ток по паре узлов.

    Аргументы:
        branch_current_map (dict): Словарь токов в ветвях.
        node_pair_list (list): Список из двух узлов.

    Возвращает:
        str: Имя тока, соответствующего данной паре узлов.
    """
    for key, value in branch_current_map.items():
        if all(elem in value for elem in node_pair_list):
            return key

def convert_voltage_to_ohm_law(voltage_names: list, voltage_map: dict, branch_current_map: dict) -> dict:
    """
    Преобразует список напряжений в выражения по закону Ома.

    Аргументы:
        voltage_names (list): Список имён напряжений.
        voltage_map (dict): Словарь напряжений.
        branch_current_map (dict): Словарь токов в ветвях.

    Возвращает:
        dict: Словарь, где ключ — имя напряжения, значение — выражение по закону Ома.
    """
    result = {}
    for voltage in voltage_names:
        if voltage in voltage_map:
            node_pair_list = voltage_map[voltage]
        elif f"-{voltage}" in voltage_map:
            node_pair_list = voltage_map[f"-{voltage}"][::-1]
        resistance = voltage[voltage.find("_")+1:]
        current = get_current_by_nodes(branch_current_map, node_pair_list)
        result[voltage] = f"({current}*{resistance})"
    return result

def solve_forbidden_current_expressions(forbidden_names: list, branch_current_map: dict, voltage_map: dict, element_nodes: dict, element_graph: dict, element_key: str, forbidden_voltage_names: list) -> dict:
    """
    Решает выражения для запрещённых токов.

    Аргументы:
        forbidden_names (list): Список имён запрещённых токов.
        branch_current_map (dict): Словарь токов в ветвях.
        voltage_map (dict): Словарь напряжений.
        element_nodes (dict): Словарь с информацией об узлах элементов.
        element_graph (dict): Словарь соединений между элементами.
        element_key (str): Имя элемента.
        forbidden_voltage_names (list): Список имён запрещённых напряжений.

    Возвращает:
        dict: Словарь выражений для запрещённых токов.
    """
    result = {}
    for elem in forbidden_names:
        node_pair_list = get_element_terminals(elem, branch_current_map)
        resistance = "(" + get_resistor_names_from_path(branch_current_map[elem], element_nodes) + ")"
        path_list = find_all_paths_in_graph(element_graph, node_pair_list[0], node_pair_list[1])
        path_list = filter_valid_element_paths(path_list, element_nodes)
        expr = get_voltage_expression_along_path(path_list, voltage_map, element_key)
        forbidden = get_forbidden_voltages(forbidden_voltage_names, expr)
        if not forbidden:
            result[elem] = f"({expr})/{resistance}"
            continue
        else:
            formula = convert_voltage_to_ohm_law(forbidden, voltage_map, branch_current_map)
            for key, value in formula.items():
                expr = expr.replace(key, value)
        result[elem] = f"({expr})/{resistance}"
    return result

def generate_circuit_equations(can_be: list, cant_be: list, need_to_find: list, branch_current_map: dict,
                voltage_map: dict, element_nodes: dict, element_graph: dict) -> tuple:
    """
    Генерирует уравнения для токов и напряжений в схеме.

    Аргументы:
        can_be (list): Список переменных, которые могут быть найдены.
        cant_be (list): Список переменных, которые не могут быть найдены.
        need_to_find (list): Список переменных, которые нужно найти.
        branch_current_map (dict): Словарь токов в ветвях.
        voltage_map (dict): Словарь напряжений.
        element_nodes (dict): Словарь с информацией об узлах элементов.
        element_graph (dict): Словарь соединений между элементами.

    Возвращает:
        tuple: Кортеж из двух словарей — уравнения для токов и для напряжений.
    """
    u_set = {}
    i_set = {}
    i_max_set = []
    for elem in need_to_find[1]:
        if len(branch_current_map) == 1:
            def get_u_from_path(path, voltage_map):
                expr = []
                for i in range(0, len(path)-1):
                    pos1 = path[i]
                    pos2 = path[i+1]
                    for key, val in voltage_map.items():
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
            resistance = get_resistor_names_from_path(branch_current_map[elem], element_nodes)
            voltage = get_u_from_path(branch_current_map[elem], voltage_map)
            i_set[elem] = simplify(f"({voltage})/({resistance})")
        else:
            equation = get_kirchhoff_current_equation(elem, branch_current_map)
            forbidden = get_forbidden_currents(cant_be, equation.rhs)
            if not forbidden:
                i_set[elem] = equation
                break
            else:
                solved = solve_forbidden_current_expressions(forbidden, branch_current_map, voltage_map, element_nodes, element_graph, elem, cant_be)
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
        def get_u_from_path(path, voltage_map):
            expr = []
            for i in range(0, len(path)-1):
                pos1 = path[i]
                pos2 = path[i+1]
                for key, val in voltage_map.items():
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
        if len(branch_current_map) == 1:
            if elem in voltage_map.keys():
                node_pair_list = voltage_map[elem]
            else:
                node_pair_list = voltage_map[elem][::-1]
            path = find_all_paths_in_graph(element_graph, node_pair_list[0], node_pair_list[1])
            path.remove(node_pair_list)
            formula = get_u_from_path(path[0], voltage_map)
            forbidden = get_forbidden_voltages(cant_be, formula)
            x = convert_voltage_to_ohm_law(forbidden, voltage_map, branch_current_map)
            for key, value in x.items():
                formula = formula.replace(key, value)
            u_set[elem] = simplify(formula)
        else:
            node_pair_list = voltage_map[elem]
            path_list = find_all_paths_in_graph(element_graph, node_pair_list[0], node_pair_list[1])
            path_list.remove(node_pair_list)
            path_list = filter_valid_element_paths(path_list, element_nodes)
            formulas = []
            for key, path in path_list.items():
                formulas.append(get_u_from_path(path, voltage_map))
            is_good_formula = False
            while True:
                if is_good_formula:
                    break
                forbidden = get_forbidden_voltages(cant_be, formulas[0])
                u_eq = convert_voltage_to_ohm_law(forbidden, voltage_map, branch_current_map)
                for key, value in u_eq.items():
                    formulas[0] = formulas[0].replace(key, f"{value}")
                for key, value in i_set.items():
                    if key in formulas[0]:
                        formulas[0] = formulas[0].replace(key, f"{value}")
                if get_forbidden_currents(cant_be, simplify(formulas[0])) == []:
                    is_good_formula = True
            u_set[elem] = simplify(formulas[0])
    print(i_set, u_set, sep='\n')
    return i_set, u_set