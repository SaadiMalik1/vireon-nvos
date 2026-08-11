# DEPRECATED: vireon-corpus

This package is deprecated as of v2.0.0. Use `vireon_moabb.datasets` instead.

The audit found that `vireon-corpus/vireon_corpus/dataset_manager.py` ignored
its `key` parameter and returned identical data for all 7 declared datasets.
Rather than fix this, VIREON now delegates all dataset loading to MOABB,
which has a mature, well-tested dataset registry.

## Migration

### Before (v1.x)
```python
from vireon_corpus import DatasetManager
dm = DatasetManager()
data = dm.load_dataset("physionet_bci", subject=1)
```

### After (v2.0+)
```python
from vireon_moabb.datasets import get_dataset
dataset = get_dataset("BNCI2014_001")
data = dataset.get_data(subjects=[1])
```

This file will be removed in v2.1.0.
