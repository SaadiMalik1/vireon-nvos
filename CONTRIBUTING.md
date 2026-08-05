# Contributing to VIREON

Thank you for your interest in contributing to **VIREON** (Validation, Integrity, Research Engine for Open Neuro Interfaces). VIREON is dedicated to building an open-source, empirically validated, real-data-backed neurotechnology platform.

---

## 1. Code of Conduct

All contributors, maintainers, and community members are expected to adhere to our Code of Conduct:
- Maintain a welcoming, inclusive, and professional environment.
- Demonstrate scientific integrity: never hardcode constants, fabricate metrics, or bypass tests.
- Provide constructive feedback during code and peer reviews.

---

## 2. Getting Started & Development Workflow

### 2.1 Branching Strategy
All work must take place on dedicated task branches:
- For Real Data Milestone A: `abc/R<NN>-<slug>`
- For Corpus Expansion Milestone B: `abc/W<NN>-<slug>`
- For Productization Milestone C: `abc/P<NN>-<slug>`

### 2.2 Test-Driven Development (TDD) Required
1. **Red**: Write a failing unit test in `tests/` or `vireon-verification/literature/` first.
2. **Green**: Implement the minimal code required to pass the test.
3. **Refactor**: Clean up the implementation while preserving passing test assertions.

### 2.3 Strict Determinism (DeterministicRNG)
VIREON enforces 100% reproducible execution. **Never use `np.random.*` directly in any core module or test**. Always instantiate `DeterministicRNG(seed)`:

```python
from vireon_core.runtime.rng import DeterministicRNG

rng = DeterministicRNG(seed=42)
samples = rng.normal(loc=0.0, scale=1.0, size=(100, 250))
```

### 2.4 Paper Reproduction Standards
If contributing a literature reproduction test:
- Must cite the paper's **DOI** in the file docstring.
- Must include a clear pass condition matching published literature results.
- Must not hardcode expected values or mock predictions.

---

## 3. Submitting a Pull Request (PR)

Before submitting a Pull Request:
1. Run the entire test suite:
   ```bash
   pytest --tb=short -q
   ```
2. Verify all automated grep gates pass cleanly:
   ```bash
   ! rg 'evidence_hash\s*=\s*""' vireon-validation/ vireon-core/
   ! rg "PARQUET_STUB_DATA" vireon-validation/
   ! rg "np\.random\.(normal|uniform|choice)" vireon-validation/vireon_validation/perturbations/
   ```
---

## 4. Issue Reporting & Triage Workflow

If you discover a bug or want to propose a new feature or literature reproduction:

1. **Check Existing Issues**: Search GitHub Issues to avoid creating duplicates.
2. **Use Issue Templates**: Select the appropriate template from `.github/ISSUE_TEMPLATE/`:
   - `bug_report.md`: For reporting reproducible errors or test failures.
   - `feature_request.md`: For proposing new algorithms, datasets, or platform features.
   - `algorithm_proposal.md`: For submitting new literature papers to reproduce.
3. **Provide Minimum Reproducible Example (MRE)**: Attach a minimal Python snippet demonstrating the bug using `DeterministicRNG`.

---

## 5. Style Guidelines & Code Formatting

- **PEP 8 Compliance**: Follow standard Python formatting. Limit lines to 100 characters.
- **Type Annotations**: Provide explicit type hints for all public function arguments and return values (`List`, `Dict`, `Tuple`, `Optional`, `np.ndarray`).
- **Docstrings**: Use Google-style docstrings for all classes, methods, and modules.
- **Lin's CCC Threshold**: All signal processing algorithms must pass Lin's $CCC \ge 0.99$ against reference standard implementations.

---

## 7. Git Commit Message & Tagging Conventions

VIREON enforces standardized commit messages to enable automated semantic release drafting and changelog generation:

### 7.1 Commit Message Structure
```
<type>(<scope>): <short summary>

<optional detailed description>

Fixes: #<issue_number>
```

### 7.2 Allowed Types
- `feat`: A new algorithm, dataset loader, or platform feature.
- `fix`: A bug fix or tolerance correction in a test assertion.
- `docs`: Documentation updates (user guide, developer guide, API reference).
- `test`: Adding or refactoring literature reproduction tests or validation benchmarks.
- `refactor`: Internal code refactoring without public API breakage.
- `ci`: Changes to GitHub Actions workflows or grep gates.

---

## 8. Final Contribution Checklist

- [ ] Code is formatted cleanly and adheres to PEP 8.
- [ ] All randomness uses `DeterministicRNG` with a fixed seed.
- [ ] All new algorithms are cross-validated against reference standards ($CCC \ge 0.99$).
- [ ] New literature tests cite paper DOIs in docstrings.
- [ ] All 15 success criteria and CI grep gates pass.
