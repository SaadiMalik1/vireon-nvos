# Philosophy

The philosophy of VIREON can be summarized in three core tenets.

## 1. Validation, Not Simulation
We do not believe that building a perfect, molecule-by-molecule simulation of the human brain is computationally feasible or strictly necessary for neurotechnology development.

Simulation asks: *"Can we perfectly recreate reality?"*
Validation asks: *"Can we perfectly bound the failure modes of our technology?"*

VIREON is adversarial. It generates digital twins specifically designed to break your decoders by injecting mathematically defined noise and physiological artifacts.

## 2. Capability over Class
Scientific computation often suffers from massive inheritance trees. In VIREON, what an object *is* matters far less than what it *can do*. If a plugin declares that it can calculate Power Spectral Density and enforce Wide-Sense Stationarity, the kernel will route data to it, regardless of its underlying inheritance structure.

## 3. Explicit Scientific Contracts
A function signature `def process(data: numpy.ndarray) -> numpy.ndarray` is scientifically meaningless. VIREON mandates that the physics, biology, and math assumed by the code must be explicitly declared as a `ScientificContract` that the Evidence Engine can verify against an ontological Knowledge Graph.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
