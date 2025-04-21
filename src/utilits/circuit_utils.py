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
    

