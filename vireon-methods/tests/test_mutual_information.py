import numpy as np
from vireon_methods.connectivity.vireon_mutual_information import VireonMutualInformation


def test_mutual_information_basic():
    """Test basic compute and compute_matrix functionality."""
    rng = np.random.default_rng(42)
    x = rng.normal(0, 1, 500)
    y = rng.normal(0, 1, 500)

    mi_calc = VireonMutualInformation(k=4)
    mi = mi_calc.compute(x, y)
    assert isinstance(mi, float)
    assert mi >= 0.0

    data = np.vstack([x, y])
    mi_mat = mi_calc.compute_matrix(data)
    assert mi_mat.shape == (2, 2)
    assert np.isclose(mi_mat[0, 1], mi_mat[1, 0])
