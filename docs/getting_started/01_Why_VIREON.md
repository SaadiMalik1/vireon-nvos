# Why VIREON?

When neuroscientists develop a new algorithm (e.g., a novel Motor Imagery classification pipeline), they typically write a script using `MNE-Python`, `SciPy`, and `scikit-learn` to process their dataset. They get an accuracy of 82%, publish a paper, and share the code.

But critical scientific questions remain unanswered:
- **Was it reproducible?**
- **Under which perturbations does it degrade?**
- **What are its exact failure modes?**
- **Does it generalize across hardware systems?**
- **Has anyone independently reproduced it?**
- **What statistical agreement exists across populations?**
- **Can another lab safely replay the entire pipeline?**

This is the gap VIREON solves.

## From Software to Scientific Infrastructure

VIREON is not just another signal processing library. It is a **Native Neuroscience Evidence Engine**.

Instead of manually stitching datasets and algorithms together, VIREON introduces a mathematically formalized **Scientific Contract**. Algorithms are bound to their stated assumptions. 

### The VIREON Workflow
1. **Dataset Definition**: The user declares the dataset.
2. **Scientific Contract**: The algorithm (`IPlugin`) declares its physiological assumptions (e.g., stationary covariance).
3. **Cartesian Benchmark Matrix**: The system runs the algorithm against the dataset while programmatically injecting perturbations (white noise, channel dropouts, missing packets).
4. **Evidence Bundles**: The outputs are cryptographic hashes containing the method provenance, software environment, and multivariate performance metrics (CCC, SDR).
5. **Evidence Graph**: The resulting evidence is pushed into a queryable semantic knowledge graph.
6. **Meta-Analysis**: Historical algorithms are compared.
7. **Operational Envelope**: VIREON objectively charts the exact domain where the algorithm is mathematically safe to use.

With VIREON, the question is no longer *"What accuracy did my algorithm achieve?"* but instead *"What evidence supports trusting this algorithm, under which conditions, and with what limitations?"*
