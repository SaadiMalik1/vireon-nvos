import pytest
import gc

@pytest.fixture(autouse=True)
def memory_leak_cleanup():
    """
    Automatically cleans up matplotlib figures and forces garbage collection 
    after every test to prevent memory leaks during large test suite runs.
    """
    yield
    try:
        import matplotlib.pyplot as plt
        plt.close('all')
    except ImportError:
        pass
    
    # Force garbage collection to prevent memory ballooning
    gc.collect()
