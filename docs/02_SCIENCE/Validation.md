# Validation

Validation is the process of determining if an algorithm or model meets the requirements for a specific intended use.

## Cross-Validation vs. Adversarial Validation
Standard machine learning cross-validation (e.g., k-fold) on a single dataset only proves that a model hasn't overfit the training set. It does *not* prove that the model will generalize to new hardware, new subjects, or new artifact profiles.

VIREON implements **Adversarial Validation**. The target model is frozen, and `vireon-validation` iteratively searches the parameter space of the `vireon-models` artifact generators to find the exact threshold where the model fails (the operating envelope).