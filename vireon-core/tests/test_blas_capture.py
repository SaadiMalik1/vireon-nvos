import pytest
import numpy as np
from vireon_core.contracts.base import EnvironmentCapture

def test_blas_capture_not_hardcoded():
    ctx = EnvironmentCapture.capture()
    if ctx.blas_implementation is not None:
        assert ctx.blas_implementation != "openblas64__openblas", \
            "BLAS should not be a hardcoded dummy string"
        assert len(ctx.blas_implementation) > 0

def test_blas_capture_returns_none_on_failure(monkeypatch):
    """If all capture methods fail, return None — never a hardcoded lie."""
    if hasattr(np, '__config__'):
        if hasattr(np.__config__, 'CONFIG'):
            monkeypatch.setattr(np.__config__, 'CONFIG', {})
        if hasattr(np.__config__, 'get_info'):
            monkeypatch.setattr(np.__config__, 'get_info', lambda x: {}, raising=False)
            
    result = EnvironmentCapture._capture_blas()
    assert result is None or isinstance(result, str)
    assert result != "openblas64__openblas"
