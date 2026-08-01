# First Validation: Motor Imagery

To demonstrate the power of VIREON, we will run a canonical Campaign evaluating Common Spatial Patterns (CSP) for Motor Imagery.

Instead of writing a custom Python script, you define the experiment declaratively using a `manifest.yaml`:

```yaml
campaign:
  name: Motor Imagery CSP Demo
  
  dataset:
    provider: SyntheticMotorImagery
    
  workflow:
    - Bandpass
    - CAR
    - CSP
    - LDA
    
  perturbations:
    - WhiteNoise
    - LineNoise
    - ChannelDropout
    
  evaluation:
    - RMSE
    - CCC
    - Accuracy
    
  report:
    markdown: true
    figures: true
```

## Running the Campaign

Execute the campaign from your terminal:

```bash
vireon campaign run manifest.yaml
```

Under the hood, VIREON reads the manifest, instantiates the `SyntheticMotorImageryProvider`, loads the Native `CSPPlugin`, and constructs a `BenchmarkMatrix`. The matrix automatically generates execution permutations combining the dataset with every defined perturbation.

## The Output

The execution generates a complete evidence package:
- `evidence.json`: Cryptographic metrics of the run.
- `evidence_graph.json`: Nodes mapping the algorithm to the literature it supports.
- `evidence.md`: A publication-ready report including Bland-Altman and Robustness curves.

By standardizing this output, any laboratory worldwide can run your manifest and mathematically guarantee whether their system reproduced your claims.
