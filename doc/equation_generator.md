# equation_generator.py

## Назначение

Модуль для генерации уравнений Кирхгофа (токов и напряжений) на основе структуры электрической схемы. Использует символьные вычисления для получения аналитических выражений.

## Основные функции

- `is_sublist(main_list, sublist)` — проверка, является ли sublist подсписком main_list.
- `normalize_operators(expression)` — нормализация операторов в строке выражения.
- `find_all_paths_in_graph(element_graph, start, end, path=None)` — поиск всех путей между двумя узлами в графе.
- `filter_valid_element_paths(path_list, element_nodes)` — фильтрация путей, соответствующих элементам схемы.
- `get_current_by_nodes(branch_current_map, node_pair_list)` — определение тока по паре узлов.
- `convert_voltage_to_ohm_law(voltage_names, voltage_map, branch_current_map)` — преобразование напряжений по закону Ома.
- `generate_circuit_equations(...)` — генерация системы уравнений для токов и напряжений.

## Входные и выходные данные

- Вход: структура схемы, список ветвей, карта токов и напряжений, граф соединений.
- Выход: словари с уравнениями для токов и напряжений.
