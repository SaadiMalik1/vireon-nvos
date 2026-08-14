# VIREON Reproducibility Guide — Step-by-Step Instructions

## 1. Quick Reproduction (< 5 Minutes)

To verify the entire VIREON validation suite and literature reproductions on your local system:

```bash
# 1. Clone the repository
git clone https://github.com/SaadiMalik1/vireon-nvos.git
cd vireon-nvos

# 2. Install dependencies
pip install -r requirements.txt

# 3. Execute full validation test suite
pytest --tb=no -q

# 4. Execute literature reproduction suite
pytest vireon-verification/literature/ -v
```

---

## 2. Evidence Registry Bundle Generation

To generate and verify evidence bundles:

```bash
python examples/first_validation/demo.py
python examples/multi_subject_validation.py
```

---

## 3. Regulatory Audit Package Export

To export the complete regulatory audit binder (FDA GMLP, SOUP Inventory, Validation Master Plan, ROI Case Study):

```bash
python examples/example_regulatory_submission.py
```
