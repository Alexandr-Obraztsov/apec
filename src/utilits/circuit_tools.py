from collections import defaultdict

def get_inductors_and_capacitors(circuit) -> list:
    """
    Возвращает список имён всех индуктивностей и конденсаторов в схеме.

    Аргументы:
        circuit: Объект схемы (circuit), содержащий элементы схемы.

    Возвращает:
        list: Список имён индуктивностей и конденсаторов.
    """
    inductors_and_capacitors = []
    for name in circuit.element_names:
        if 'L' in name or 'C' in name:
            inductors_and_capacitors.append(name)
    return inductors_and_capacitors

def split_variable_list(variables_str: str) -> list:
    """
    Разделяет строку переменных на отдельные переменные.

    Аргументы:
        variables_str (str): Строка с переменными.

    Возвращает:
        list: Список переменных.
    """
    delimiter = ']+'
    variables_str = variables_str.strip('[]')
    variable_list = variables_str.split(delimiter)
    variable_list = [var.strip() for var in variable_list]
    if variable_list and variable_list[0].startswith('['):
        variable_list[0] = variable_list[0][1:]
    if variable_list and variable_list[0].endswith(']'):
        variable_list[0] = variable_list[0][:-1]
    for i in range(len(variable_list)):
        if variable_list[i] and variable_list[i][0] == "[":
            variable_list[i] = variable_list[i][1:]
    return variable_list

def add_element_to_division(variable_list: list, divider_element: str) -> list:
    """
    Добавляет элемент в делитель для каждой переменной.

    Аргументы:
        variable_list (list): Список переменных.
        divider_element (str): Элемент, который добавляется в делитель.

    Возвращает:
        list: Новый список переменных с добавленным делителем.
    """
    new_variable_list = []
    for var in variable_list:
        if '/' in var:
            elem = "(" + var[var.find('/ ( +')+5:]
            var = var.replace(f"{var[var.find('/ '):]}", f"/({divider_element}*{elem})")
        else:
            var = f'({var})/({divider_element})'
        new_variable_list.append(var)
    return new_variable_list

def get_element_nodes_dict(circuit) -> dict:
    """
    Возвращает словарь с узлами для каждого элемента схемы.

    Аргументы:
        circuit: Объект схемы (circuit), содержащий элементы схемы.

    Возвращает:
        dict: Словарь, где ключ — имя элемента, значение — список его узлов и параметров.
    """
    element_nodes_dict = {}
    for circuit_element in circuit.elements:
        if circuit_element.PREFIX == 'V':
            element_nodes_dict[circuit_element.name] = circuit_element.node_names + [circuit_element.dc_value.value]
        elif circuit_element.PREFIX == 'L':
            element_nodes_dict[circuit_element.name] = circuit_element.node_names + [circuit_element.inductance.value]
        elif circuit_element.PREFIX == 'I':
            element_nodes_dict[circuit_element.name] = circuit_element.node_names + [circuit_element.current.value]
        elif circuit_element.PREFIX == 'R':
            element_nodes_dict[circuit_element.name] = circuit_element.node_names + [circuit_element.resistance.value]
        elif circuit_element.PREFIX == 'C':
            element_nodes_dict[circuit_element.name] = circuit_element.node_names + [circuit_element.capacitance.value]
        elif circuit_element.PREFIX == 'X':
            element_nodes_dict[f"Line {circuit_element.name}"] = circuit_element.node_names
        else:
            return "Error at PREFIX"
    return element_nodes_dict

def get_node_connections(circuit) -> dict:
    """
    Возвращает словарь соединений между узлами схемы.

    Аргументы:
        circuit: Объект схемы (circuit), содержащий элементы схемы.

    Возвращает:
        dict: Словарь соединений между узлами.
    """
    node_connections = defaultdict(set)
    for circuit_element in circuit.elements:
        parts = str(circuit_element).split(' ')
        node_connections[parts[1]].add(parts[2])
        node_connections[parts[2]].add(parts[1])
    return node_connections

def find_junction_nodes(graph: dict) -> list | int:
    """
    Находит вершины в графе, из которых выходит более двух рёбер.
    """
    junction_nodes = []
    for node in graph.keys():
        if len(graph[node]) > 2:
            junction_nodes.append(node)
    return junction_nodes if junction_nodes else 0

def find_single_path(graph_in: dict) -> list:
    """
    Находит единственный путь, проходящий через все вершины графа.
    """
    path = [0]
    graph = defaultdict(set)
    for key, values in graph_in.items():
        graph[int(key)] = {int(value) for value in values}
    while len(path) < len(graph):
        neighbors = graph[path[-1]]
        next_node = next(iter(neighbors - set(path)), None)
        if next_node is None:
            raise ValueError('No single path through all nodes')
        path.append(next_node)
    return [str(node) for node in path]

def find_all_paths_between_nodes(graph: dict, start: str, end: str, path: list = None) -> list:
    """
    Находит все возможные пути между двумя узлами в графе.
    """
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
            new_paths = find_all_paths_between_nodes(graph, node, end, path)
            for new_path in new_paths:
                if end in new_path:
                    paths.append(new_path)
    return paths

def assign_branch_names(branches: list, nodes_list: dict) -> dict:
    """
    Присваивает имена ветвям на основе списка узлов.
    """
    branch_names = {}
    for branch in branches:
        for i in range(len(branch) - 1):
            pos1 = branch[i]
            pos2 = branch[i + 1]
            name = ""
            for key, value in nodes_list.items():
                if sorted(value[0] + value[1]) == sorted(pos1 + pos2):
                    if "X" in key:
                        break
                    elif "R" in key or "V" in key:
                        name = f"I_{key}"
                        break
                    elif "C" in key or "L" in key:
                        name = f"I_{key}"
                        if branch in branch_names.values():
                            branch_names = {name if v == branch else k: v for k, v in branch_names.items()}
                        else:
                            branch_names[name] = branch
                        break
            if branch not in branch_names.values():
                branch_names[name] = branch
    return branch_names

def calculate_branches(nodes_list: dict, connection_list: dict) -> dict:
    """
    Вычисляет ветви схемы на основе списка узлов и соединений.
    """
    from itertools import combinations
    branches = []
    nodes = find_junction_nodes(connection_list)
    if nodes == 0:
        branches.append(find_single_path(connection_list) + ['0'])
        branches = assign_branch_names(branches, nodes_list)
    else:
        node_combinations = list(combinations(nodes, 2))
        node_combinations = [comb for comb in node_combinations if (comb[1], comb[0]) not in node_combinations]
        for comb in node_combinations:
            branches += find_all_paths_between_nodes(connection_list, comb[0], comb[1])
        branches = assign_branch_names(branches, nodes_list)
    return branches

def substitute_element_values(formula: str, nodes: dict) -> str:
    """
    Подставляет численные значения элементов в формулу.
    
    Аргументы:
        formula (str): Формула для подстановки значений.
        nodes (dict): Словарь с информацией об элементах и их значениях.

    Возвращает:
        str: Формула с подставленными значениями.
    """
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
    

