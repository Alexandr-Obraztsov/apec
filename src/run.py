from PySpice.Spice.Netlist import Circuit
from entities.transmission_line import TransmissionLine as LineCircuit
from entities.circuit_simulation import CircuitSimulation
from PySpice.Unit import *

circuit = Circuit('1')
circuit.subcircuit(LineCircuit('Line'))
circuit.V(1, 1, circuit.gnd, 100@u_V)
circuit.R(1, 1, 2, 1@u_Ω)
circuit.L(1, 2, 3, 0.001@u_H)
circuit.R(3, 3, 5, 10@u_Ohm)
circuit.C(1, 5, circuit.gnd, 0.001@u_F)
circuit.X(1, 'Line', 3, 4)
circuit.R(2, 4, circuit.gnd, 2@u_Ohm)
sim = CircuitSimulation(circuit)
sim.print_connections()	
sim.print_currents()
sim.print_voltages()

sim.set_initial_conditions({'L1': 100.0, 'C1': 100.0})
sim.analyze()