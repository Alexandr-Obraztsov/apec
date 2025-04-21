import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()
from PySpice.Spice.Netlist import Circuit, SubCircuit
from PySpice.Unit import *

class Line(SubCircuit):
    NODES = ('n1','n2')
    def __init__(self, name):
        SubCircuit.__init__(self, name, *self.NODES)
        self.R(1, 'n1', 'n2', 0@u_Ohm)



