# External Researcher Quickstart Guide — Reproducing VIREON in < 30 Minutes

Welcome to **VIREON**. This quickstart guide enables independent researchers, auditors, and clinical scientists to reproduce all scientific claims, literature reproductions, and evidence bundles in under 30 minutes.

---

## Step 1: Environment Setup (2 Minutes)

Ensure Python 3.10+ is installed on your Linux / macOS / Windows system.

```bash
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos
pip install -r requirements.txt
```

---

## Step 2: Running Literature Reproductions (5 Minutes)

Run all 22 literature reproduction tests across 5 subfields (BCI, Clinical, Sleep, Epilepsy, Cognitive):

```bash
pytest vireon-verification/literature/ -v
```

Expected output: `35 passed in 4.86s`

---

## Step 3: Running Real-World Use Case Examples (10 Minutes)

Execute any of VIREON's 13 real-world use case scripts:

```bash
# Hardware assessment
python examples/example_hardware_validation.py

# Clinical trial tracking
python examples/example_clinical_trial.py

# Multi-dataset benchmark across 4 open datasets
python examples/example_multidataset_benchmark.py

# Algorithm comparison (Welch vs Multitaper)
python examples/example_algorithm_comparison.py

# Real-time streaming simulation
python examples/example_realtime_bci.py
```

---

## Step 4: Verification of Audit Deliverables (5 Minutes)

Review regulatory binders and corporate ROI case studies:
- `docs/corporate/roi_case_study.md`
- `docs/regulatory/fda_gmlp_compliance.md`
- `docs/regulatory/soup_inventory.md`
- `docs/regulatory/validation_master_plan.md`
- `EVIDENCE_PORTFOLIO.md`

---

## Step 5: Full Automated Suite Execution (5 Minutes)

Run the full automated test suite containing 360+ tests:

```bash
pytest --tb=no -q
```

All tests will pass with 0 failures, proving 100% deterministic reproducibility.
