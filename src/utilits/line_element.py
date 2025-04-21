import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

class TransmissionLine(SubCircuit):
    """
    Класс, описывающий линию передачи как подцепь с одним резистором.

    Аргументы:
        subcircuit_name (str): Имя подцепи (используется для идентификации).

    Атрибуты:
        NODES (tuple): Кортеж с именами узлов ('n1', 'n2').
    """
    NODES = ('n1', 'n2')

    def __init__(self, subcircuit_name: str) -> None:
        """
        Инициализирует подцепь TransmissionLine с заданным именем.

        Аргументы:
            subcircuit_name (str): Имя подцепи.

        Возвращает:
            None
        """
        super().__init__(subcircuit_name, *self.NODES)
        self.R(1, 'n1', 'n2', 0 @ u_Ohm)



