# The Scientific Pipeline

In traditional data science, a pipeline is usually an imperative script (`train.py`) that loads data, calls `.fit()`, and computes an accuracy score. 

In VIREON, a pipeline is a **Directed Acyclic Graph (DAG) of Scientific Contracts**.

## The Nodes
Every node in the pipeline is an instantiated `IPlugin` (e.g., an Artifact Generator, a Feature Extractor, a Decoder).

## The Edges
Every edge in the pipeline is an `IScientificObject` (e.g., an `ISignal` containing EEG data). Edges are strictly typed. You cannot pass raw numpy arrays between nodes.

## Pipeline Resolution
When a user defines a scenario (e.g., "Test Decoder X against Dataset Y with Artifact Z"), the core engine dynamically builds the pipeline. 
If Decoder X requires input capabilities that Dataset Y cannot provide, the pipeline resolution fails immediately, preventing invalid scientific testing.