import numpy as np
from vireon_methods.machine_learning.csp import CSPPlugin
from vireon_core.contracts.plugin import ScientificReadinessLevel

def test_csp_returns_correct_shape():
    X = np.random.default_rng(0).normal(size=(20, 8, 250))
    y = np.array([0,1]*10)
    csp = CSPPlugin(n_components=4)
    features = csp.execute({"signal": X, "labels": y})
    assert features.shape == (20, 8)  # 2 * n_components

def test_csp_features_are_log_variance():
    X = np.random.default_rng(0).normal(size=(20, 8, 250))
    y = np.array([0,1]*10)
    csp = CSPPlugin(n_components=2)
    features = csp.execute({"signal": X, "labels": y})
    
    # Verify features are log variance manually
    filters = csp._filters
    X_trans = np.zeros((20, filters.shape[1], 250))
    for i in range(20):
        X_trans[i] = filters.T @ X[i]
        
    log_var = np.log(np.var(X_trans, axis=-1))
    assert np.allclose(features, log_var)

def test_csp_compatible_with_lda():
    X = np.random.default_rng(0).normal(size=(40, 8, 250))
    y = np.array([0,1]*20)
    csp = CSPPlugin(n_components=4)
    features = csp.execute({"signal": X, "labels": y})
    
    from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
    lda = LinearDiscriminantAnalysis()
    lda.fit(features, y)
    assert lda.score(features, y) >= 0.5

def test_csp_srl_is_srl2():
    csp = CSPPlugin()
    assert csp.srl == ScientificReadinessLevel.SRL_2
