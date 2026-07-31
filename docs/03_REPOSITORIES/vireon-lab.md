# vireon-lab

`vireon-lab` is the interactive and user-facing entry point to the ecosystem. It provides CLI tools and Jupyter notebooks for exploring, validating, and reproducing research.

## Reproducibility CLI
The crown jewel of `vireon-lab` is the `vireon reproduce` command.

- **Status**: [FULLY IMPLEMENTED]
- The Reproducibility Engine allows a researcher to pass a DOI or paper identifier. The engine fetches the canonical Evidence Graph for that paper, rebuilds the exact digital twins, orchestrates the DAG, and outputs a validation report comparing the current numerical output to the historical baseline.

### Usage
```bash
vireon reproduce 10.1016/j.neuroimage.2023.111111 --factor 10
```
*(The `--factor` flag forces a 10x adversarial permutation grid to test if the paper's claims hold up under noise).*

## Interactive Twin Dashboards
- **Status**: [STUBBED]
- A planned interactive UI (via Streamlit or Dash) for visualizing Hardware Digital Twins (e.g. turning a dial to increase packet loss and watching the real-time PSD degrade) is fully stubbed and not yet implemented.