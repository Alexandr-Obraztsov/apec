from collections import defaultdict

def get_List_LC(circuit):
    ans = []
    for i in circuit.element_names:
        if 'L' in i:
            ans.append(i)
        elif 'C' in i:
            ans.append(i)
    return ans

def split_variables(s):
    delimiter = ']+'
    # Избавляемся от скобок в начале и конце строки, если они есть:
    s = s.strip('[]')
    # Разделяем строку на подстроки по заданному разделителю:
    variables = s.split(delimiter)
    # Удаляем возможные пробелы в начале и конце каждой подстроки:
    variables = [var.strip() for var in variables]
    # Если первая переменная начинается со скобки "[", удаляем ее:
    if variables[0].startswith('['):
        variables[0] = variables[0][1:]
    # Если первая переменная заканчивается скобкой "]", удаляем ее:
    if variables[0].endswith(']'):
        variables[0] = variables[0][:-1]
    # Возвращаем список переменных:
    for i in range(len(variables)):
        if variables[i][0] == "[":
            variables[i] = variables[i][1:]
            
    return variables

def add_elem_to_division(variables, c):
    new_variables = []
    for var in variables:
        # Если в переменной есть деление "/", добавляем C1 в скобки:
        if '/' in var:
            elem = "(" + var[var.find('/ ( +')+5:]
            var = var.replace(f"{var[var.find('/ '):]}", f"/({c}*{elem})")
        # Если в переменной нет деления, добавляем C1 в знаменатель:
        else:
            var = f'({var})/({c})'
        new_variables.append(var)
    return new_variables


def get_elem_nodes(circuit):
    ans = {}
    for i in circuit.elements:
        if i.PREFIX == 'V':
            ans[i.name] = i.node_names + [i.dc_value.value]
        elif i.PREFIX == 'L':
            ans[i.name] = i.node_names + [i.inductance.value]
        elif i.PREFIX == 'I':
            ans[i.name] = i.node_names + [i.current.value]
        elif i.PREFIX == 'R':
            ans[i.name] = i.node_names + [i.resistance.value]
        elif i.PREFIX == 'C':
            ans[i.name] = i.node_names + [i.capacitance.value]
        elif i.PREFIX == 'X':
            ans[f"Line {i.name}"] = i.node_names
        else:
            return "Error at PREFIX"
    return ans

def get_connections(circuit):
    l = []
    ans = defaultdict(set)
    for i in circuit.elements:
        l.append(str(i).split(' '))
    for i in l:
        ans[i[1]].add(i[2])
        ans[i[2]].add(i[1])
    return ans
    

