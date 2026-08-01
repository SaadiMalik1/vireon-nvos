# Scientific Methodology Handbook

## 1. Core Paradigm
VIREON enforces a methodology where computational neurotechnology is treated as a falsifiable scientific hypothesis. Every algorithm must state its assumptions, and the framework ensures those assumptions are not violated during execution.

## 2. Uncertainty Propagation
Uncertainty must be tracked end-to-end. If an EEG hardware model specifies a noise floor of `X`, and a spectral estimation algorithm has a variance of `Y`, the final output measurement must reflect the combined propagated uncertainty `f(X, Y)`. 

## 3. The Role of Digital Twins
Digital Twins in VIREON (`vireon-models`) are not full biophysical simulations of the brain. They are phenomenological statistical models calibrated against real-world patient datasets (e.g. `CHB-MIT`, `TUH EEG`). They exist solely to test if an algorithm's agency bounds hold true across population variance.

## 4. Literature Verification
Algorithms must cite peer-reviewed DOIs. VIREON utilizes the `LiteratureVerifier` to parse DOIs and ensure the paper explicitly supports the algorithmic parameters used.

## 5. Required Evidence for New Algorithms
Any new algorithmic method introduced to VIREON must have:
- Mathematical proofs of bounds.
- Comparison against standard reference implementations (e.g., MNE-Python, EEGLAB).
- A corresponding validation scenario demonstrating failure conditions.


## Phase E Implementation Status
> [!NOTE]
