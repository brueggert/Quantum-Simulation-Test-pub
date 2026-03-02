Brueggert_Report_Quantum_Simulation_Test.pdf:  Report in response to the Quantum Simulation Test.  
	Please read the entire report before running any code.

simulate_amplitude.txt and simulate_amplitude_mps_src.txt require having their files extensions changed 
	to .py in both cases.  (Had been .txt to ensure email delivery.)  Both files are designed to be run 
	from within the \circuit_gen\ directory.  These are the tesnor network and MPS versions, respectively,
	of Python 3.12 code for execution.
	
P1_little_peak.qasm (4 qubits), P2_swift_rise.qasm (28 qubits), peaked_circuit_diff=37_2.qasm (37 qubits):
	delta-peaked quantum circuits (OPEN QASM 2.0 format) with respective qubit circuit sizes.  These are
	designed to be placed in the ..\ directory from the provided code execution files, i.e. in the same 
	directory as \circuit_gen directory is located (within \quantum-dev-hiring-test\)