from hypothesis import given, strategies as st, assume
import numpy as np
from vireon_methods.spatial.vireon_csp import VireonCSP


@given(
    n_pairs=st.integers(10, 30),
    n_channels=st.integers(4, 12),
    n_samples=st.integers(100, 300),
    n_components=st.sampled_from([2, 4]),
)
def test_csp_output_dimensions(n_pairs, n_channels, n_samples, n_components):
    """CSP output feature dimension must equal n_components for even n_components."""
    assume(n_components <= n_channels)
    n_epochs = n_pairs * 2
    rng = np.random.default_rng(42)
    X = rng.normal(size=(n_epochs, n_channels, n_samples))
    y = np.array([0, 1] * n_pairs)

    csp = VireonCSP(n_components=n_components)
    csp.fit(X, y)
    feats = csp.transform(X)
    assert feats.shape == (n_epochs, n_components)
