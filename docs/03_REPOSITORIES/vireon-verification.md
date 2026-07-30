# vireon-verification

`vireon-verification` is the CI/CD test suite.

While `vireon-validation` tests the *science* (does the decoder fail when noise is added?), `vireon-verification` tests the *math* (does the optimized Rust Welch PSD output the exact same float64 array as the `vireon-reference` Python Welch PSD?).

No Pull Request can be merged into `vireon-methods` unless the `vireon-verification` GitHub Actions pass with numerical equivalence.