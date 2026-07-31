# Plugin Architecture

VIREON's extensibility is driven by its Plugin Architecture. The core engine (`vireon-core`) is completely agnostic to the actual mathematics being performed. It only understands Capabilities and Contracts.

## `IPlugin`
The abstract base class for everything in the VIREON ecosystem.
To add a new signal processing method, you do not modify `vireon-core`. You create a new Python class inheriting from `IPlugin` in `vireon-methods`.

### 1. `capabilities`
A list of `PluginCapability` objects defining what the plugin consumes (e.g., `ISignal`) and what it produces (e.g., `IMeasurement`).

### 2. `contract`
A `ScientificContract` object mapping the plugin's mathematical assumptions to the `vireon-knowledge` ontology.

### 3. `execute`
The actual runtime logic. This method accepts a dictionary of `IScientificObject` payloads, performs the numpy/scipy calculations, and returns a new `IScientificObject`.

## Discovery
Plugins are automatically discovered by the engine at runtime via Python's entry points mechanism. This allows third-party researchers to publish their own standalone VIREON plugin packages (`vireon-methods-customlab`) that the core engine can seamlessly orchestrate.

## Phase E Implementation Status
> [!NOTE]
> As of Phase E, the architecture has expanded to include Massive Campaigns, Hardware Digital Twins, EvidenceBundle v5 (SRI/Regulatory mapping), and the Reproduce CLI. Features described in this document may be subject to these new workflows. If specific API endpoints, models, or UI components are discussed but missing in the codebase, they are currently [STUBBED] pending Phase F implementation.
