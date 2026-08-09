import warnings
import vireon_methods.spectral.welch
import vireon_methods.machine_learning.csp
import vireon_methods.machine_learning.ica


def test_deprecated_welch_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plugin = vireon_methods.spectral.welch.WelchPSDPlugin()
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert plugin is not None


def test_deprecated_csp_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plugin = vireon_methods.machine_learning.csp.CSPPlugin()
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert plugin is not None


def test_deprecated_ica_import():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plugin = vireon_methods.machine_learning.ica.ICAPlugin()
        assert len(w) >= 1
        assert any(issubclass(item.category, DeprecationWarning) and "deprecated" in str(item.message).lower() for item in w)
        assert plugin is not None
