# VIREON Setup Guide

Welcome to the VIREON project! This guide will help you set up the monorepo for development and validation.

## Prerequisites

- Python 3.14+
- Git

## 1. Clone the Repository

```bash
git clone <repository_url>
cd VIREON
```

## 2. Python Environment Setup

We recommend using a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the core dependencies:
```bash
pip install -r requirements.txt
```

### Install Monorepo Packages

Install all VIREON packages in editable mode:
```bash
pip install -e .
```

## 3. Running the Test Suite

To ensure everything is working correctly:
```bash
pytest
```

## 4. Datasets and Benchmarks

To fetch standard datasets or run benchmarks, use the CLI tools provided in `vireon-lab`:
```bash
python -m vireon_lab.cli.dataset_manager --fetch eegbci
python -m vireon_validation.benchmarks --scenarios-dir vireon-validation/vireon_validation/benchmarks/scenarios --output-dir results/
```
