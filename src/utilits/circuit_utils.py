from collections import defaultdict

def get_lc_element_names(circuit):
    lc_elements = []
    for name in circuit.element_names:
        if 'L' in name or 'C' in name:
            lc_elements.append(name)
    return lc_elements

def split_variable_list(variable_string):
    delimiter = ']+'
    variable_string = variable_string.strip('[]')
    variables = variable_string.split(delimiter)
    variables = [var.strip() for var in variables]
    if variables and variables[0].startswith('['):
        variables[0] = variables[0][1:]
    if variables and variables[0].endswith(']'):
        variables[0] = variables[0][:-1]
    for i in range(len(variables)):
        if variables[i] and variables[i][0] == "[":
            variables[i] = variables[i][1:]
    return variables

def add_element_to_division(variables, element):
    new_variables = []
    for var in variables:
        if '/' in var:
            elem = "(" + var[var.find('/ ( +')+5:]
            var = var.replace(f"{var[var.find('/ '):]}", f"/({element}*{elem})")
        else:
            var = f'({var})/({element})'
        new_variables.append(var)
    return new_variables

def get_element_nodes(circuit):
    element_nodes = {}
    for element in circuit.elements:
        if element.PREFIX == 'V':
            element_nodes[element.name] = element.node_names + [element.dc_value.value]
        elif element.PREFIX == 'L':
            element_nodes[element.name] = element.node_names + [element.inductance.value]
        elif element.PREFIX == 'I':
            element_nodes[element.name] = element.node_names + [element.current.value]
        elif element.PREFIX == 'R':
            element_nodes[element.name] = element.node_names + [element.resistance.value]
        elif element.PREFIX == 'C':
            element_nodes[element.name] = element.node_names + [element.capacitance.value]
        elif element.PREFIX == 'X':
            element_nodes[f"Line {element.name}"] = element.node_names
        else:
            return "Error at PREFIX"
    return element_nodes

def get_circuit_connections(circuit):
    connections = defaultdict(set)
    for element in circuit.elements:
        parts = str(element).split(' ')
        connections[parts[1]].add(parts[2])
        connections[parts[2]].add(parts[1])
    return connections
    

