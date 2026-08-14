import numpy as np
from vireon_core.runtime.rng import DeterministicRNG
from vireon_methods.spatial.vireon_csp import VireonCSP
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

def run_cross_subject_scenario():
    print("=== Running Cross-Subject Generalization Validation ===")
    n_subjects = 5
    n_epochs, n_channels, n_samples = 40, 8, 250
    y = np.array([0, 1] * (n_epochs // 2))
    
    subjects_data = []
    for s in range(n_subjects):
        rng = DeterministicRNG(seed=1000 + s)
        X = rng.normal(0, 1.0, (n_epochs, n_channels, n_samples))
        # Realistic inter-subject spatial mixing variability
        R_sub = rng.normal(0, 0.4, (n_channels, n_channels)) + np.eye(n_channels)
        for i in range(n_epochs):
            if y[i] == 0:
                X[i, :4] *= 1.6
            else:
                X[i, 4:] *= 1.6
            X[i] = R_sub @ X[i]
        subjects_data.append(X)
        
    # Leave-one-subject-out cross-validation
    accs = []
    for test_idx in range(n_subjects):
        train_X = np.concatenate([subjects_data[i] for i in range(n_subjects) if i != test_idx])
        train_y = np.tile(y, n_subjects - 1)
        
        test_X = subjects_data[test_idx]
        test_y = y
        
        csp = VireonCSP(n_components=4)
        train_feats = csp.fit_transform(train_X, train_y)
        test_feats = csp.transform(test_X)
        
        clf = LinearDiscriminantAnalysis()
        clf.fit(train_feats, train_y)
        acc = clf.score(test_feats, test_y)
        accs.append(acc)
        
    mean_acc = float(np.mean(accs))
    print(f"Leave-One-Subject-Out Cross-Subject Accuracy: {mean_acc * 100:.2f}%")
    assert 0.55 <= mean_acc <= 0.95, f"Cross-subject accuracy {mean_acc:.2f} not in [0.55, 0.95]"
    print("PASS: Cross-Subject Generalization Validation")

if __name__ == "__main__":
    run_cross_subject_scenario()
