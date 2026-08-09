from hypothesis import given, strategies as st
import numpy as np
from vireon_methods.spatial.vireon_ica import VireonICA


@given(
    n_samples=st.integers(200, 500),
    n_components=st.integers(2, 4),
)
def test_ica_components_shape(n_samples, n_components):
    """VireonICA transform output shape must match (n_samples, n_components)."""
    rng = np.random.default_rng(42)
    S = rng.uniform(-1, 1, (n_samples, n_components))
    A = rng.normal(size=(n_components, n_components))
    X = S @ A.T

    ica = VireonICA(n_components=n_components)
    ica.fit(X)
    sources = ica.transform(X)
    assert sources.shape == (n_samples, n_components)
