# APEC — Анализ электрических цепей с PySpice

## Описание

Этот проект предназначен для анализа и моделирования электрических цепей с помощью библиотеки PySpice, символьных вычислений (SymPy) и численного решения ОДУ. Программа строит граф цепи, определяет ветви, формирует уравнения по законам Кирхгофа, решает их и визуализирует результаты.

### Основные возможности:

- Автоматическое построение графа цепи и определение ветвей
- Генерация уравнений по законам Кирхгофа (токи/напряжения)
- Символьное и численное решение системы уравнений
- Визуализация изменения токов и напряжений во времени
- Поддержка пользовательских подцепей (например, линия передачи)

---

## Быстрый старт

1. Установите Python 3.10+.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Запустите основной скрипт:

```bash
python src/circuit_simulation.py
```

---

## Как задать схему

Схема задаётся в файле `src/circuit_simulation.py` (блок `if __name__ == "__main__":`). Пример:

```python
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *
from utilits.transmission_line import TransmissionLine as LineCircuit

circuit = Circuit('MyCircuit')
circuit.subcircuit(LineCircuit('Line'))
circuit.V(1, 1, circuit.gnd, 100@u_V)
circuit.R(1, 1, 2, 1@u_Ohm)
circuit.L(1, 2, 3, 0.001@u_H)
circuit.R(3, 3, 5, 10@u_Ohm)
circuit.C(1, 5, circuit.gnd, 0.001@u_F)
circuit.X(1, 'Line', 3, 4)
circuit.R(2, 4, circuit.gnd, 2@u_Ohm)
```

**Правила:**

- Схема должна быть связной (из любого узла можно попасть в любой другой)
- Не допускаются параллельные резисторы (но можно комбинировать с другими элементами)
- Узлы — целые числа, земля — `circuit.gnd`
- Для каждого элемента используйте уникальный номер

---

## Структура проекта

- `src/circuit_simulation.py` — основной скрипт анализа цепи
- `src/utilits/circuit_tools.py` — функции для работы с элементами, узлами, ветвями, подстановкой значений
- `src/utilits/equation_generator.py` — генерация уравнений Кирхгофа, обработка формул, фильтрация путей
- `src/utilits/plotting.py` — визуализация решений ОДУ, подстановка переменных
- `src/utilits/transmission_line.py` — определение пользовательской линии передачи (SubCircuit)
- `examples/test.py` — пример численного решения системы ОДУ
- `requirements.txt` — зависимости

---

## Основные методы и функции

### circuit_tools.py

- `get_inductors_and_capacitors(circuit)` — список всех индуктивностей и конденсаторов
- `get_element_nodes_dict(circuit)` — словарь узлов и параметров для каждого элемента
- `get_node_connections(circuit)` — граф соединений между узлами
- `calculate_branches(nodes_list, connection_list)` — определение ветвей схемы
- `substitute_element_values(formula, nodes)` — подстановка численных значений в формулу

### equation_generator.py

- `generate_circuit_equations(...)` — генерация уравнений для токов и напряжений
- `get_kirchhoff_current_equation(...)` — уравнение по первому закону Кирхгофа
- `filter_valid_element_paths(...)` — фильтрация путей по элементам

### plotting.py

- `plot_ode_system_solution(initial_conditions_dict, inductor_equations, capacitor_equations)` — построение графиков решений ОДУ

### transmission_line.py

- `TransmissionLine` — класс пользовательской линии передачи (SubCircuit для PySpice)

---

## Пример работы

После запуска `src/circuit_simulation.py`:

- Программа выведет информацию о ветвях, напряжениях
- Запросит начальные условия для индуктивностей и конденсаторов
- Построит графики изменения токов и напряжений во времени

---

## Требования

- Python 3.10+
- PySpice 1.5
- numpy, scipy, matplotlib, networkx, sympy

---

## Автор

Укажите своё имя и контакты при необходимости.
