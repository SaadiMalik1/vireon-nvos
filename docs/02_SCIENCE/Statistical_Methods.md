# Statistical Methods

Neurotechnology validation relies on robust statistical inference. A decoder that achieves 90% accuracy on a single subject dataset may be statistically insignificant if the sample size is low or the variance is high.

## Common Spatial Pattern (CSP)
CSP is a fundamental spatial filtering technique for Motor Imagery BCIs. It seeks to find a spatial projection matrix $\mathbf{W}$ that maximizes the variance of one class while minimizing the variance of the other.

Mathematically, it solves the generalized eigenvalue problem:
$$ \mathbf{\Sigma}_1 \mathbf{w} = \lambda \mathbf{\Sigma}_2 \mathbf{w} $$
Where $\mathbf{\Sigma}_1$ and $\mathbf{\Sigma}_2$ are the spatial covariance matrices of the two classes.

*Assumption*: CSP assumes that the noise covariance is stationary between the two classes. If an artifact (e.g. jaw clenching) is present in class 1 but not class 2, CSP will learn to decode the artifact, not the neural signal. VIREON validates CSP implementations by explicitly injecting asymmetric artifacts.

## Phase E Implementation Status

> [!NOTE]
> **Status: Partial (v1.0.3)**
>
> Scientific principles are implemented in vireon-core/contracts/ and vireon-knowledge/.
> Runtime contract enforcement is production-ready.