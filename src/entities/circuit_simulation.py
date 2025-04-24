import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from entities.transmission_line import TransmissionLine as LineCircuit
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from utilits.circuit_tools import get_inductors_and_capacitors, get_element_nodes_dict, get_node_connections, calculate_branches, substitute_element_values, calculate_voltages
from sympy import *
from utilits.equation_generator import generate_circuit_equations
from utilits.plotting import plot_ode_system_solution

class CircuitSimulation:
    """
    Класс для анализа переходных процессов в электрических цепях.

    Принимает готовый объект схемы (PySpice Circuit), автоматически извлекает все элементы,
    строит граф соединений, определяет ветви, формирует уравнения по законам Кирхгофа,
    запрашивает начальные условия у пользователя и решает систему ОДУ для моделирования переходного процесса.

    Основные возможности:
    - Автоматическое построение графа схемы и определение ветвей
    - Генерация уравнений для токов и напряжений (с учётом индуктивностей и конденсаторов)
    - Запрос начальных условий у пользователя
    - Численное решение системы ОДУ и построение графиков переходных процессов
    - Удобный вывод информации о структуре схемы, токах и напряжениях

    Атрибуты:
        circuit: объект схемы PySpice
        lc_list: список имён индуктивностей и конденсаторов
        nodes_list: словарь с узлами и параметрами элементов
        connection_list: граф соединений между узлами
        simulator: объект симулятора PySpice
        analysis: результат операционного анализа схемы
        need_to_find: переменные, которые нужно найти (для генерации уравнений)
        state_variables: переменные состояния (токи через L, напряжения на C)
        currents: словарь токов в ветвях
        voltages: словарь напряжений на элементах
    """
    def __init__(self, circuit):
        """
        Инициализация анализа схемы.
        Аргументы:
            circuit: объект схемы PySpice (Circuit)
        """
        self.circuit = circuit
        self.lc_list = get_inductors_and_capacitors(circuit)
        self.nodes_list = get_element_nodes_dict(circuit)
        self.connection_list = get_node_connections(circuit)
        self.simulator = circuit.simulator(temperature=25, nominal_temperature=25)
        self.analysis = self.simulator.operating_point()
        self.need_to_find = [[], []]
        self.state_variables = []
        for element in self.lc_list:
            if "L" in element:
                self.need_to_find[0].append(f"U_{str(element)}")
                self.state_variables.append(f"I_{str(element)}")
            else:
                self.need_to_find[1].append(f"I_{str(element)}")
                self.state_variables.append(f"U_{str(element)}")
        self.currents = calculate_branches(self.nodes_list, self.connection_list)
        self.voltages = calculate_voltages(self.currents, self.nodes_list)

    def print_connections(self):
        """
        Выводит на экран список соединений между узлами схемы в удобочитаемом виде.
        """
        print("\n=== Список соединений между узлами схемы ===")
        for node, connections in self.connection_list.items():
            print(f"  Узел {node}: соединён с {', '.join(map(str, connections))}")
        print("=== Конец списка соединений ===\n")

    def print_currents(self):
        """
        Выводит на экран информацию о токах в ветвях схемы.
        """
        print("\n=== Токи в ветвях схемы ===")
        if not self.currents:
            print("  Нет данных о токах.")
        else:
            for branch, current in self.currents.items():
                print(f"  Ветвь {branch}: путь {current}")
        print("=== Конец списка токов ===\n")

    def print_voltages(self):
        """
        Выводит на экран информацию о напряжениях на элементах схемы.
        """
        print("\n=== Напряжения на элементах схемы ===")
        if not self.voltages:
            print("  Нет данных о напряжениях.")
        else:
            for branch, voltage in self.voltages.items():
                print(f"  {branch}: между узлами {voltage}")
        print("=== Конец списка напряжений ===\n")

    def set_initial_conditions(self, initial_conditions: dict) -> None:
        """
        Устанавливает начальные условия для индуктивностей и конденсаторов схемы.
        Аргументы:
            initial_conditions (dict): Словарь с начальными условиями для каждого элемента.
        """
        self.initial_conditions = {}
        for key, value in initial_conditions.items():
            if "L" in key:
                self.initial_conditions[f"I_{key}"] = value
            else:
                self.initial_conditions[f"U_{key}"] = value

    def analyze(self) -> None:
        """
        Выполняет полный анализ переходного процесса:
        - Формирует систему уравнений по законам Кирхгофа
        - Подставляет численные значения элементов
        - Решает систему ОДУ и строит графики переходных процессов
        """
        if self.initial_conditions is None:
            raise ValueError("Initial conditions are not set")
        
        can_be = []
        cant_be = []
        for key in self.nodes_list:
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
        for key in self.currents:
            if "I_L" in key:
                can_be.append(f"{key}")
            if "I_C" in key or "I_R" in key or "I_V" in key:
                cant_be.append(key)
        del key
        i_set, u_set = generate_circuit_equations(
            can_be=can_be,
            cant_be=cant_be,
            need_to_find=self.need_to_find,
            branch_current_map=self.currents,
            voltage_map=self.voltages,
            element_nodes=self.nodes_list,
            element_graph=self.connection_list
        )
        il_equations = []
        uc_equations = []
        for key, value in i_set.items():
            i_set[key] = simplify(substitute_element_values(value, self.nodes_list))
            uc_equations.append(substitute_element_values(f"U_{key[2:]}' = ({i_set[key]})/{key[2:]}", self.nodes_list))
        for key, value in u_set.items():
            u_set[key] = simplify(substitute_element_values(value, self.nodes_list))
            il_equations.append(substitute_element_values(f"I_{key[2:]}' = ({u_set[key]})/{key[2:]}", self.nodes_list))
            
        plot_ode_system_solution(self.initial_conditions, il_equations, uc_equations)        
