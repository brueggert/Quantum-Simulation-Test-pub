import numpy as np
from blueqat import Circuit 
from qiskit import QuantumCircuit
from qiskit import transpile 
from qiskit.qasm2 import dumps as qasm2_dumps
from qiskit import qasm2
import sys
import quimb as qu
import quimb.tensor as qtn
from collections import Counter
from qiskit.qasm3 import loads
from qiskit_quimb import quimb_circuit

def get_index(q):
    """Return the index of a Qiskit Qubit object."""
    try:
        return q.index
    except AttributeError:
        return q._index

def read_qasm_file(file_path):
    with open(file_path, 'r') as file:
    #    qasm_code = file.read()
    #return qasm_code
    	return file.read()
    	
# ----- Helper: Convert a sample to a bitstring -----
def sample_to_bitstring(sample):
    """Convert a NumPy array (e.g. [0,1,0,...]) into a bitstring."""
    if sample.size == 0:
        return ""
    return ''.join(str(int(x)) for x in sample)

n_qubits = 37
samples = 500 # 1000 20000

qc0 = read_qasm_file('../peaked_circuit_diff=37_2.qasm')

qc0 = QuantumCircuit.from_qasm_str(qc0)

def qasm_to_quimb_tensor(qasm_string):
    """Converts a QASM string to a Quimb tensor network.

    Args:
        qasm_string (str): The QASM string representing the quantum circuit.

    Returns:
        quimb.tensor.tensor_network.TensorNetwork: The Quimb tensor network
            representing the quantum circuit.
    """

    # Parse the QASM string using Qiskit
    qc = QuantumCircuit.from_qasm_str(qasm_string)

    # Create a list to store the gate tensors
    gate_tensors = []

    # Create a dictionary to track qubit indices
    qubit_indices = {i: i for i in range(qc.num_qubits)}

    # Iterate through the gates in the circuit
    for instruction in qc.data:
        gate = instruction[0]
        qargs = instruction[1]

        # Create the gate tensor
        if gate.name == 'h':
            tensor = qu.hadamard()
            indices = [qubit_indices[qargs[0].index], f'k{qargs[0].index}']
            qubit_indices[qargs[0].index] = f'k{qargs[0].index}'
        elif gate.name == 'cx':
            tensor = qu.cnot()
            indices = [
                qubit_indices[qargs[0].index],
                qubit_indices[qargs[1].index],
                f'k{qargs[0].index}',
                f'k{qargs[1].index}',
            ]
            qubit_indices[qargs[0].index] = f'k{qargs[0].index}'
            qubit_indices[qargs[1].index] = f'k{qargs[1].index}'
        # Add more gates as needed
        else:
            raise ValueError(f"Gate '{gate.name}' not supported.")
        
        gate_tensors.append(qtn.Tensor(tensor, indices, tags=gate.name))

    # Create the initial state tensor
    initial_state = qtn.Tensor(qu.zeros(2**qc.num_qubits), tuple(range(qc.num_qubits)), tags='initial_state')

    # Build the tensor network
    tn = qtn.TensorNetwork([initial_state, *gate_tensors])
    return tn
    
tn = quimb_circuit(qc0)
final_samples = tn.sample(samples)

final_counts = Counter(final_samples)
sorted_outcomes = sorted(final_counts.items(), key=lambda x: x[1], reverse=True)

print("\nFinal sampled outcomes (top 5):")
for bstr, count in sorted_outcomes[:5]:
    print(f"{bstr}: {count}")
    
all_zero = '0' * n_qubits
most_common = sorted_outcomes[0]
second_common = None
for bstr, count in sorted_outcomes:
    if bstr != all_zero:
        second_common = (bstr, count)
        break
print("\nMost likely outcome (peak):")
print(f"{most_common[0]}: {most_common[1]}")
if second_common:
    print("\nSecond most likely outcome (excluding all zeros):")
    print(f"{second_common[0]}: {second_common[1]}")
else:
    print("\nNo second outcome found (excluding all zeros).")




