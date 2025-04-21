from scipy import *
from sympy import *

def is_sublist(lst, sub_lst):
    for i in range(len(lst) - len(sub_lst) + 1):
        if lst[i:i+len(sub_lst)] == sub_lst:
            return True
    return False

def replace_operators(f):
    # Избавление от --
    return f.replace('--', '+').replace('++', '+').replace('+-', '-').replace('-+', '-')

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

def kir1(name, currents):
    ans = ""
    for key, value in currents.items():
        if name == key:
            continue
        elif currents[name][0] == value[0]:
            ans += f"-{key}"
        elif currents[name][0] == value[len(value)-1]:
            ans+=f"+{key}"
    return Eq(simplify(f"{name}"), simplify(ans))

def check_Currents(cant_be, formula):
    ans = []
    for i in cant_be:
        if formula.has(simplify(i)):
            ans.append(i)
    return ans

def get_sides_nodes(name, graph):
    pos1 = graph[name][0]
    pos2 = graph[name][len(graph[name])-1]
    return [pos1, pos2]

def get_R_from_path(path, nodes):
    ans = []
    for i in range(len(path)-1):
        pos1 = path[i]; pos2 = path[i+1]
        for key, value in nodes.items():
            if ((pos1 == value[0] and pos2 == value[1]) or (pos1 == value[1] and pos2 == value[0])) and "R" in key:
                ans.append(key)
    return "+".join(ans)

def get_only_good_paths(paths, nodes):
    #Получить словрь для Uc Il и проверить находяться ли они в этих путях. удалить пути без них
    goods = {}
    for key, value in nodes.items():
        if "X" in key or "V" in key or "R" in key:
            continue
        else:
            goods[key] = (value[:2])
    ans = {}
    for key, i in goods.items():
        for path in paths:
            if is_sublist(path, i) or path == i or path[::-1] == i or is_sublist(path, i[::-1]):
                ans[key] = path
                break
    return ans

def give_Voltage_in_path(paths, voltages, name):
    #Выражени по пути  U12 = U10 + U02   
    name = name[name.find('_')+1:]
    xpath = paths[name]
    ans = []
    for i in range(len(xpath)-1):
        pos1 = xpath[i]; pos2 = xpath[i+1]
        for key, value in voltages.items():
            if [pos1, pos2] == value:
                ans.append(key)
            elif [pos1, pos2] == value[::-1]:
                ans.append(f"-{key}")
    ans = "+".join(ans)
    ans = replace_operators(ans)
    return ans

def check_U(cant_be, formula):
    ans = []
    for i in cant_be:
        if i in formula:
            ans.append(i)
    return ans

def get_I_from_R(currents, poses):
    for key, value in currents.items():
        if all(elem in value for elem in poses):
            return key

def give_equal_for_U(x, voltages, currents):
    ans = {}
    for i in x:
        if i in voltages:
            poses = voltages[i]
        elif f"-{i}" in voltages:
            poses = voltages[f"-{i}"][::-1]
        R = i[i.find("_")+1:]
        I = get_I_from_R(currents, poses)
        ans[i] = f"({I}*{R})"

    return ans

def get_equal_for_I(bad_list, currents, voltages, nodes_list, connections, name, cant_be):
    ans = {}
    for elem in bad_list:
        poses = get_sides_nodes(elem, currents)
        R = "(" + get_R_from_path(currents[elem], nodes_list) +")"
        paths = find_all_paths(connections, poses[0], poses[1])
        paths = get_only_good_paths(paths, nodes_list)
        paths = give_Voltage_in_path(paths, voltages, name)
        x = check_U(cant_be, paths)
        if x == []:
            ans[elem] = f"({paths})/{R}"
            continue
        else:
            formula = give_equal_for_U(x, voltages, currents)
            for key, value in formula.items():
                paths = paths.replace(key, value)
        ans[elem] = f"({paths})/{R}"
    return ans


def get_formul(can_be, cant_be, need_to_find, currents,
                voltages, nodes_list, connections):
    #FOR IC
    U_set = {}
    I_set = {}
    """
    1. Выразить ток в С по 1 крихгофа
    2. Проверить токи, на нормальность
    3. Если ок, то готово иначе
    4. Выразить каждый ток через U/R
    5. Выразить U через нормальные парамметры
    ЗАМЕТКА
    При выражении U лучше всего брать через IC, чтобы просто потом вынести
    """
    I_MAX_SET = []
    for elem in need_to_find[1]:
        if len(currents) == 1:
            def get_U_from_path(path, voltages):
                ans = []
                for i in range(0, len(path)-1):
                    pos1 = path[i]; pos2 = path[i+1]
                    for key, val in voltages.items():
                        if "R" in key or "X" in key:
                            continue
                        elif [pos1, pos2] == val:
                            if "V" in key:
                                ans.append(f"-{key}")
                                break
                            ans.append(f"-{key}")
                            break
                        elif [pos2, pos1] == val:
                            if "V" in key:
                                ans.append(f"+{key}")
                                break
                            ans.append(f"+{key}")
                            break
                ans = "+".join(ans)
                ans = replace_operators(ans)
                return ans
            
            R = get_R_from_path(currents[elem], nodes_list) 
            U = get_U_from_path(currents[elem], voltages)
            I_set[elem] = simplify(f"({U})/({R})")
        else:
            I = kir1(elem, currents)
            bad_elem = (check_Currents(cant_be, I.rhs))
            if bad_elem == []:
                I_set[elem] = I
                break
                #OK
            else:
                f = get_equal_for_I(bad_elem, currents, voltages, nodes_list, connections, elem, cant_be)
                I_eq = []
                for key, value in f.items():
                    I_eq.append(Eq(simplify(key), simplify(value)))
                for i in I_eq:
                    I = I.subs(i.lhs, i.rhs)
                    I_set[elem] = solve(I, I.lhs)[0]
                I_MAX_SET.append(I)
                for i in I_eq:
                    I_MAX_SET.append(i)

    #FOR UL
    """
    1.Найти все пути для UL
    2.Посчитать кол-во плохие элементов для каждого пути.
    3.Для найменьшего пути(по кол-ву плохих эл-ов) выражать UR
    4.Если все ок, то возвращай иначе сохранить новую формулу. и по циклу так делать и пытаться выражать
    """
    for elem in need_to_find[0]:
        def get_U_from_path(path, voltages):
                ans = []
                for i in range(0, len(path)-1):
                    pos1 = path[i]; pos2 = path[i+1]
                    for key, val in voltages.items():
                        if "X" in key:
                            continue
                        elif [pos1, pos2] == val:
                            ans.append(f"+{key}")
                            break
                        elif [pos2, pos1] == val:
                            ans.append(f"-{key}")
                            break
                ans = "+".join(ans)
                ans = replace_operators(ans)
                return ans
                
        if len(currents) == 1:
            if elem in voltages.keys():
                poses = voltages[elem]
            else:
                poses = voltages[elem][::-1]
            path = find_all_paths(connections, poses[0], poses[1])
            path.remove(poses)
            formula = get_U_from_path(path[0], voltages)
            bad_elem = check_U(cant_be, formula)
            x = give_equal_for_U(bad_elem, voltages, currents)
            for key, value in x.items():
                formula = formula.replace(key, value)
            U_set[elem] = simplify(formula)
        else:
            poses = voltages[elem]
            paths = find_all_paths(connections, poses[0], poses[1]); paths.remove(poses)
            paths = get_only_good_paths(paths, nodes_list)
            F = []
            for key, path in paths.items():
                F.append(get_U_from_path(path, voltages))
            is_good_formula = False
            while True:
                if is_good_formula:
                    break
                bad_elem = check_U(cant_be, F[0])
                U_eq = give_equal_for_U(bad_elem, voltages, currents)
                for key, value in U_eq.items():
                    F[0] = F[0].replace(key, f"{value}")
                for key, value in I_set.items():
                    if key in F[0]:
                        F[0] = F[0].replace(key, f"{value}")
                if check_Currents(cant_be, simplify(F[0])) == []:
                    is_good_formula = True
            U_set[elem] = simplify(F[0])

    print(I_set, U_set, sep = '\n')
    return I_set, U_set