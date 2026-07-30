# API Reference

This documentation is auto-generated from the Python docstrings within the VIREON source code. It represents the strict interfaces and objects that plugins must implement to interact with the capability-based kernel.

## Contracts

The contracts module defines the `IPlugin` interface that all methodologies, hardware models, and artifact generators must implement. It also defines the `ScientificContract` that explicitly bounds the applicability of the plugin.

::: vireon_core.contracts.plugin
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3

## Base Objects

The base module defines the fundamental `IScientificObject` payloads (like `ISignal`) that traverse the plugin DAG.

::: vireon_core.contracts.base
    options:
      show_root_heading: true
      show_source: true
      heading_level: 3
