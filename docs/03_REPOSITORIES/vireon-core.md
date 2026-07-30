# vireon-core

`vireon-core` is the absolute foundation of the NVOS ecosystem.

## Design Philosophy
This repository contains **zero** scientific logic, **zero** signal processing algorithms, and **zero** physiological models. 
It is strictly an orchestration and contract enforcement engine.

## Key Modules

### `vireon_core.contracts`
Defines the `IPlugin` and `IScientificObject` abstract base classes. Any Python object that inherits from `IPlugin` can be loaded dynamically by the kernel.

### `vireon_core.engine`
The execution router. It accepts a declarative YAML manifest (a Goal), parses the available capabilities across all registered plugins, and dynamically constructs the execution DAG.

### `vireon_core.evidence`
The provenance tracker. As the DAG executes, this module intercepts the inputs and outputs, hashes them, and serializes the state of the `ScientificContract` into an immutable `IEvidence` JSON-LD bundle.