# **Quantum Simulation Test Assignment**

### **Objective**

The purpose of this test is to evaluate:

* Understanding of **quantum circuit simulation** and **tensor network methods**.
* Practical experience with **Python scientific libraries** such as **PyTorch** and **Autoray**.
* Ability to assess and report **computational performance requirements** for large-scale quantum simulations.

---

### **Requirements**

1. **Circuit Workflow Analysis**

   * Review the provided **`circuit_generation` workflow**.
   * Identify the data structures used to represent the circuit (e.g., MPS, tensor network, dense statevector).

2. **Amplitude Calculation**

   * Compute the **probability amplitude** of the computational basis state:
     [
     |0001000001101100001011110111111110110
     ]
     for a **37-qubit peaked quantum circuit**.
   * Ensure correctness by validating against smaller test circuits where exact amplitudes are tractable.

3. **Implementation**

   * Write a **Python script** to perform this computation. The script should:

     * Parse the generated circuit.
     * Construct the **tensor network representation**.
     * Contract the network efficiently to extract the desired amplitude.
     * Support multiple backends (e.g., **NumPy**, **PyTorch**) via **Autoray** for both CPU and GPU execution.

4. **Performance Evaluation**

   * Measure and report the **computational requirements** of the simulation, including:

     * **Runtime** on CPU and/or GPU.
     * **Memory usage** (RAM/VRAM) during contraction.
     * Expected scaling behavior for larger qubit sizes (e.g., 40+ qubits).
   * Provide an estimate of the **minimum hardware specifications** required for this task (CPU cores, GPU model, memory).

---

### **Deliverables**

* A Python script (`simulate_amplitude.py`) implementing the amplitude calculation.
* A short **report** (Markdown or PDF) including:

  * Circuit workflow explanation.
  * Results of the amplitude calculation.
  * Performance benchmarks and hardware requirements.