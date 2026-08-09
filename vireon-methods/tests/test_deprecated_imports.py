import sys
import importlib
import warnings
import pytest
import vireon_methods.spectral.welch
import vireon_methods.machine_learning.csp
import vireon_methods.machine_learning.ica


def test_deprecated_welch_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(vireon_methods.spectral.welch)
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert vireon_methods.spectral.welch.WelchPSDPlugin is not None


def test_deprecated_csp_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(vireon_methods.machine_learning.csp)
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert vireon_methods.machine_learning.csp.CSPPlugin is not None


def test_deprecated_ica_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        importlib.reload(vireon_methods.machine_learning.ica)
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert vireon_methods.machine_learning.ica.ICAPlugin is not None
