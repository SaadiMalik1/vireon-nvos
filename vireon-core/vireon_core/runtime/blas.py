"""BLAS thread pinning for deterministic execution.

Ensures that BLAS operations (numpy, scipy) use a fixed number of threads,
preventing non-deterministic floating-point summation order across machines.
"""
import os
from contextlib import contextmanager


@contextmanager
def pinned_blas_threads(num_threads: int = 1):
    """Pin BLAS threads for deterministic float-summation order.

    Sets OMP_NUM_THREADS, MKL_NUM_THREADS, OPENBLAS_NUM_THREADS,
    NUMEXPR_NUM_THREADS, and VECLIB_MAXIMUM_THREADS to the specified
    number of threads. Also applies threadpoolctl if available.

    Args:
        num_threads: Number of threads to use (default: 1 for full determinism)

    Usage:
        with pinned_blas_threads(1):
            # All BLAS operations in this block use 1 thread
            result = np.dot(a, b)
    """
    env_vars = [
        'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
        'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS',
    ]
    old_values = {k: os.environ.get(k) for k in env_vars}

    for k in env_vars:
        os.environ[k] = str(num_threads)

    try:
        try:
            from threadpoolctl import threadpool_limits
            with threadpool_limits(limits=num_threads):
                yield
        except ImportError:
            # threadpoolctl not available — env vars are the fallback
            yield
    finally:
        for k, v in old_values.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
