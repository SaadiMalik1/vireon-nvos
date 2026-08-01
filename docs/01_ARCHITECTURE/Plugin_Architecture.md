# Scientific Contracts & Plugins

Algorithms in VIREON are not just functions; they are `IPlugin` modules bound to a Scientific Contract. They explicitly declare their physiological and mathematical assumptions (e.g., stationary covariance, linear mixing). If a dataset violates these assumptions, the engine will mathematically isolate the failure mode.

## Phase E Capabilities
In Phase E, this architectural component is fully active. The execution model supports authentic biological datasets alongside Digital Twins, generating EvidenceBundles that map back to originating literature.
