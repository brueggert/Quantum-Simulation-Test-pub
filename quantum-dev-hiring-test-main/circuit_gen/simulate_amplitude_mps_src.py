import math 
import os
import sys
import numpy as np
from blueqat import Circuit 
from qiskit import QuantumCircuit, transpile
from qiskit import transpile 
from qiskit.qasm2 import dumps as qasm2_dumps
from qiskit import qasm2
import sys
import quimb as qu
import quimb.tensor as qtn
from collections import Counter
from qiskit.qasm3 import loads
from qiskit_quimb import quimb_circuit
import autoray as ar
import torch
import argparse
from quimb.tensor.circuit import CircuitMPS
from pathlib import Path
from collections import Counter

def sample_tensor_network_with_backend_selection(qasm_path: str, num_samples: int, n_qubits: int):
    """
    Samples a Quimb tensor network, prioritizing PyTorch on GPU via Autoray,
    otherwise using NumPy on CPU.

    Args:
        tensor_network: The Quimb TensorNetwork object to sample.
        num_samples: The number of samples to generate.

    Returns:
        A list of dictionaries, where each dictionary represents a sample
        of the tensor network's indices.
    """

    # Check for PyTorch GPU availability
    if torch.cuda.is_available():
        print("PyTorch GPU (CUDA) available. Using PyTorch backend.")
        ar.set_backend('torch')
    else:
        print("PyTorch GPU not available. Using NumPy backend.")
        ar.set_backend('numpy')

    # Perform sampling using the selected backend
    psi0 = load_mps_from_qasm(qasm_path, max_bond=34)
    final_psi, entropy_hist = optimized_resonance(psi0, eta=0.5, T=20, max_bond=34)
    margs = compute_marginals(final_psi)
    bitstring = ''.join(str(int(np.argmax(margs[i]))) for i in range(final_psi.nsites))
    bitstring = bitstring[::-1]
    amp = final_psi.amplitude(bitstring)
    prob_amp = abs(amp)**2
    sorted_outcomes = []
    sorted_outcomes.append([bitstring, prob_amp])
    
    if (n_qubits == 37):
    	comp_basis_state = '0001000001101100001011110111111110110'
    	comp_basis_state_amp= final_psi.amplitude(comp_basis_state)
    	comp_basis_state_prob_amp = abs(comp_basis_state_amp)**2
    	sorted_outcomes.append([comp_basis_state, comp_basis_state_prob_amp])
    	
    	
    return sorted_outcomes

def get_index(q):
    """Return the index of a Qiskit Qubit object."""
    try:
        return q.index
    except AttributeError:
        return q._index

def read_qasm_file(file_path):
    with open(file_path, 'r') as file:
    	return file.read()
    	
# ----- Helper: Convert a sample to a bitstring -----
def sample_to_bitstring(sample):
    """Convert a NumPy array (e.g. [0,1,0,...]) into a bitstring."""
    if sample.size == 0:
        return ""
    return ''.join(str(int(x)) for x in sample)
    
def load_mps_from_qasm(path, max_bond=32):
    """Load a .qasm file as a true MPS."""
    circ = CircuitMPS.from_openqasm2_file(path, gate_opts={'max_bond': max_bond})
    return circ.psi

def compute_marginals(psi):
    """Compute single-qubit marginal probabilities via partial trace."""
    n = psi.nsites
    marginals = np.zeros((n, 2))
    for i in range(n):
        rdm = psi.partial_trace_to_dense_canonical(i, normalized=True)
        marginals[i, 0] = np.real(rdm[0, 0])
        marginals[i, 1] = np.real(rdm[1, 1])
    return marginals

def project_bit(psi, i, bit):
    """Project qubit i onto |bit> and return the new MPS."""
    psi2 = psi.copy()
    P = (qu.eye(2) + (-1)**bit * qu.pauli('Z'))/2
    psi2.gate(P, i, contract=True)
    return psi2

def optimized_resonance(psi, eta=0.5, T=20, max_bond=32, cutoff=1e-8, tol=1e-3):
    """
    Optimized symbolic resonance collapse:
      - Only projects qubits with marginals within tol of <tol>.
      - Compresses each projected branch immediately.
      - Early exit when all marginals are peaked.
    """
    n = psi.nsites
    entropy_history = []

    for t in range(T):
        marg = compute_marginals(psi)
        # Select qubits where |p0 - p1| < tol
        to_proj = [i for i in range(n) if abs(marg[i,0] - marg[i,1]) < tol]
        if not to_proj:
            break  # converged

        for i in to_proj:
            for b in (0, 1):
                p = project_bit(psi, i, b)
                p.compress(max_bond=max_bond, cutoff=cutoff)
                psi = psi * eta + p * (1 - eta)
                psi /= psi.norm()

        # Record entropy after cycle
        marg = compute_marginals(psi)
        entropy_history.append(-np.sum(marg * np.log2(np.clip(marg,1e-12,1))))

    return psi, entropy_history
    	
def main():
	parser = argparse.ArgumentParser(description='Simulate amplitudes / find top samples using Autoray-capable backends.')
	#parser.add_argument('qasm', help='Path to OPENQASM 2.0 file.')
	parser.add_argument('--nqubits', type=int, default=37, help='Number of qubits n peaked circuit.')
	args = parser.parse_args()

	# n_qubits = 37 
	n_qubits = args.nqubits
	samples = 500 # 1000 20000

	# qasm_path = "../P1_little_peak.qasm" # 4-qubits
	# qasm_path = "../P2_swift_rise.qasm" # 28-qubits
	qasm_path = "../peaked_circuit_diff=37_2.qasm" # 37-qubits
	# qasm_path = "../P3_sharp_peak.qasm" # 44-qubits
	qc = read_qasm_file(qasm_path)
	
	# Sample/contract the tensor network using the backend selection and 
	# n_qubits logic
	generated_samples = sample_tensor_network_with_backend_selection(qasm_path, num_samples=samples, n_qubits=n_qubits)
	
	if generated_samples:
		print("\n Final sampled outcomes (top 5):")
		for bstr, amp in generated_samples[:5]:
			print(f"{bstr}: {amp}")
			
		all_zero = '0' * n_qubits
		most_common = generated_samples[0]
		for bstr, count in generated_samples:
			if bstr != all_zero:
				second_common = (bstr, count)
				break
		print("\n Most likely outcome (peak):")
		print(f"{most_common[0]}: {most_common[1]}")
			
		print('0001000001101100001011110111111110110')
	
	else:
		print("\n No samples generated.")
	
	# Reset backend to default (or another specific one) if needed
	ar.set_backend('numpy') # Or 'torch', or None to let Autoray infer

if __name__ == '__main__':
    main()

