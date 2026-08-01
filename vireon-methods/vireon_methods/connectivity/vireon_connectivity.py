import numpy as np
from scipy.signal import welch, csd, hilbert, butter, filtfilt
from vireon_core.contracts.plugin import ScientificContractViolation

class VireonCoherence:
    """Magnitude-squared coherence: |Pxy|² / (Pxx * Pyy)."""
    def compute(self, X: np.ndarray, fs: float, band: tuple = None) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation("NaN or Inf detected.", violated_assumption="finite_values", details="", remediation="")
            
        n_channels = X.shape[0]
        coh_matrix = np.eye(n_channels)
        
        Pxx_list = []
        for i in range(n_channels):
            f, Pxx = welch(X[i], fs=fs)
            Pxx_list.append((f, Pxx))
            
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                f, Pxy = csd(X[i], X[j], fs=fs)
                Pxx = Pxx_list[i][1]
                Pyy = Pxx_list[j][1]
                
                Cxy_f = np.abs(Pxy)**2 / (Pxx * Pyy)
                
                if band is not None:
                    idx = np.logical_and(f >= band[0], f <= band[1])
                    Cxy = np.mean(Cxy_f[idx])
                else:
                    Cxy = np.mean(Cxy_f)
                    
                coh_matrix[i, j] = Cxy
                coh_matrix[j, i] = Cxy
                
        return coh_matrix

class VireonImaginaryCoherence:
    """Imaginary coherence: |imag(Pxy)| / sqrt(Pxx * Pyy)."""
    def compute(self, X: np.ndarray, fs: float, band: tuple = None) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation("NaN or Inf detected.", violated_assumption="finite_values", details="", remediation="")
            
        n_channels = X.shape[0]
        icoh_matrix = np.zeros((n_channels, n_channels))
        
        Pxx_list = []
        for i in range(n_channels):
            f, Pxx = welch(X[i], fs=fs)
            Pxx_list.append((f, Pxx))
            
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                f, Pxy = csd(X[i], X[j], fs=fs)
                Pxx = Pxx_list[i][1]
                Pyy = Pxx_list[j][1]
                
                icxy_f = np.abs(np.imag(Pxy)) / np.sqrt(Pxx * Pyy)
                
                if band is not None:
                    idx = np.logical_and(f >= band[0], f <= band[1])
                    icxy = np.mean(icxy_f[idx])
                else:
                    icxy = np.mean(icxy_f)
                    
                icoh_matrix[i, j] = icxy
                icoh_matrix[j, i] = icxy
                
        return icoh_matrix

class VireonPLV:
    """Phase Locking Value: |mean(exp(1j * (phi_i - phi_j)))|."""
    def compute(self, X: np.ndarray, fs: float, band: tuple) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation("NaN or Inf detected.", violated_assumption="finite_values", details="", remediation="")
            
        n_channels = X.shape[0]
        
        b, a = butter(4, band, btype='bandpass', fs=fs)
        X_filt = filtfilt(b, a, X, axis=-1)
        
        X_analytic = hilbert(X_filt, axis=-1)
        phase = np.angle(X_analytic)
        
        plv_matrix = np.eye(n_channels)
        
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                delta_phase = phase[i] - phase[j]
                plv = np.abs(np.mean(np.exp(1j * delta_phase)))
                plv_matrix[i, j] = plv
                plv_matrix[j, i] = plv
                
        return plv_matrix

class VireonPLI:
    """Phase Lag Index: |mean(sign(imag(exp(1j*(phi_i - phi_j)))))|."""
    def compute(self, X: np.ndarray, fs: float, band: tuple) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation("NaN or Inf detected.", violated_assumption="finite_values", details="", remediation="")
            
        n_channels = X.shape[0]
        
        b, a = butter(4, band, btype='bandpass', fs=fs)
        X_filt = filtfilt(b, a, X, axis=-1)
        
        X_analytic = hilbert(X_filt, axis=-1)
        phase = np.angle(X_analytic)
        
        pli_matrix = np.zeros((n_channels, n_channels))
        
        for i in range(n_channels):
            for j in range(i + 1, n_channels):
                delta_phase = phase[i] - phase[j]
                pli = np.abs(np.mean(np.sign(np.imag(np.exp(1j * delta_phase)))))
                pli_matrix[i, j] = pli
                pli_matrix[j, i] = pli
                
        return pli_matrix

class VireonAEC:
    """Amplitude Envelope Correlation: Pearson correlation of Hilbert envelopes."""
    def compute(self, X: np.ndarray, fs: float, band: tuple) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X)
        if np.any(np.isnan(X)) or np.any(np.isinf(X)):
            raise ScientificContractViolation("NaN or Inf detected.", violated_assumption="finite_values", details="", remediation="")
            
        n_channels = X.shape[0]
        
        b, a = butter(4, band, btype='bandpass', fs=fs)
        X_filt = filtfilt(b, a, X, axis=-1)
        
        X_analytic = hilbert(X_filt, axis=-1)
        env = np.abs(X_analytic)
        
        aec_matrix = np.corrcoef(env)
        
        return aec_matrix
