import numpy as np
import time
from typing import Dict, Any, Tuple
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    cohen_kappa_score,
    confusion_matrix
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

class DecoderEvaluator:
    """
    Evaluates Brain-Computer Interface decoders using rigorous cross-validation
    and extracts a comprehensive suite of classification metrics.
    """
    
    @classmethod
    def evaluate(cls, data: np.ndarray, sample_rate: float, labels: np.ndarray = None) -> Dict[str, float]:
        """
        Extracts features (CSP if mne is available, else Bandpower/Variance) and
        evaluates them using a cross-validated classifier (LDA).
        """
        # Segment data into mock trials for evaluation
        X, y = cls._prepare_trials(data, sample_rate, labels)
        if len(np.unique(y)) < 2 or len(y) < 4:
            return cls._empty_metrics()

        try:
            import mne
            from mne.decoding import CSP
            has_mne = True
        except ImportError:
            raise RuntimeError(
                "MNE is required for DecoderEvaluator. CSP feature extraction "
                "is necessary for scientific validity. Please install mne."
            )

        # Reshape X for MNE CSP: (n_epochs, n_channels, n_times)
        # Currently X is (n_epochs, n_channels, n_times) from _prepare_trials
        
        cv = StratifiedKFold(n_splits=min(5, len(y) // 2), shuffle=True, random_state=42)
        
        # CSP + LDA Pipeline
        # We use fewer components if we have few channels
        n_components = min(4, X.shape[1])
        clf = make_pipeline(CSP(n_components=n_components, reg=None, log=True, norm_trace=False), 
                            StandardScaler(), 
                            LinearDiscriminantAnalysis())

        y_true_all = []
        y_pred_all = []
        y_prob_all = []
        
        start_time = time.time()
        for train_idx, test_idx in cv.split(X, y):
            X_train, y_train = X[train_idx], y[train_idx]
            X_test, y_test = X[test_idx], y[test_idx]
            
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)
            y_prob = clf.predict_proba(X_test)[:, 1] if len(np.unique(y)) == 2 else clf.predict_proba(X_test)
            
            y_true_all.extend(y_test)
            y_pred_all.extend(y_pred)
            y_prob_all.extend(y_prob)
            
        training_time = time.time() - start_time
        
        y_true = np.array(y_true_all)
        y_pred = np.array(y_pred_all)
        y_prob = np.array(y_prob_all)
        
        # Compute metrics
        metrics = {
            "decoder_accuracy": float(accuracy_score(y_true, y_pred)),
            "decoder_balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
            "decoder_cohen_kappa": float(cohen_kappa_score(y_true, y_pred)),
            "decoder_training_time_sec": float(training_time)
        }
        
        if len(np.unique(y_true)) == 2:
            metrics["decoder_precision"] = float(precision_score(y_true, y_pred, zero_division=0))
            metrics["decoder_recall"] = float(recall_score(y_true, y_pred, zero_division=0))
            metrics["decoder_f1"] = float(f1_score(y_true, y_pred, zero_division=0))
            try:
                metrics["decoder_roc_auc"] = float(roc_auc_score(y_true, y_prob))
            except ValueError:
                metrics["decoder_roc_auc"] = 0.5
                
            # Specificity / Sensitivity
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            metrics["decoder_specificity"] = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
            metrics["decoder_sensitivity"] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            
        return metrics

    @staticmethod
    def _prepare_trials(data: np.ndarray, sample_rate: float, labels: np.ndarray = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Segments a continuous multi-channel array into discrete epochs (trials) of length 1 second.
        Returns X (epochs, channels, times) and y (epochs).
        """
        n_samples = data.shape[0]
        n_channels = data.shape[1] if data.ndim == 2 else 1
        
        if n_channels == 1:
            data = data.reshape(-1, 1)
            
        window_size = int(sample_rate)
        n_trials = n_samples // window_size
        
        if n_trials < 2:
            return np.array([]), np.array([])
            
        X = np.zeros((n_trials, n_channels, window_size))
        y = np.zeros(n_trials)
        
        for i in range(n_trials):
            start = i * window_size
            end = start + window_size
            # Shape: (channels, times) for MNE
            X[i, :, :] = data[start:end, :].T
            if labels is None:
                # Mock label based on block design (e.g. alternating blocks of 2 trials)
                y[i] = (i // 2) % 2
            else:
                # Majority vote for this window if labels provided
                y[i] = int(np.median(labels[start:end]))
                
        return X, y

    @staticmethod
    def _empty_metrics() -> Dict[str, float]:
        return {
            "decoder_accuracy": 0.5,
            "decoder_balanced_accuracy": 0.5,
            "decoder_cohen_kappa": 0.0,
            "decoder_training_time_sec": 0.0
        }
