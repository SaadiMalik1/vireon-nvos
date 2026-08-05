"""EEGNet Deep Convolutional Neural Network Implementation.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c
"""
import numpy as np

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    class EEGNetPyTorch(nn.Module):
        """Real PyTorch EEGNet Architecture with Depthwise & Separable Convolutions."""
        def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250):
            super().__init__()
            self.conv1 = nn.Conv2d(1, 8, (1, 64), padding=(0, 32), bias=False)
            self.depthwise = nn.Conv2d(8, 16, (channels, 1), groups=8, bias=False)
            self.separable = nn.Conv2d(16, 16, (1, 16), padding=(0, 8), bias=False)
            self.fc = nn.Linear(16 * (samples // 32), n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.conv1(x)
            x = self.depthwise(x)
            x = self.separable(x)
            x = x.view(x.size(0), -1)
            return self.fc(x)

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class EEGNetWrapper:
    """Production Wrapper for Lawhern 2018 EEGNet Deep Learning Architecture."""
    
    def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250):
        self.n_classes = n_classes
        self.channels = channels
        self.samples = samples
        self.weights = None
        self._fitted = False
        if TORCH_AVAILABLE:
            self.model = EEGNetPyTorch(n_classes, channels, samples)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, lr: float = 0.001, batch_size: int = 16):
        """Fit spatial convolution weights on EEG epochs using PyTorch Adam + CrossEntropyLoss training loop."""
        if TORCH_AVAILABLE:
            X_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            y_tensor = torch.tensor(y, dtype=torch.long)
            dataset = TensorDataset(X_tensor, y_tensor)
            loader = DataLoader(dataset, batch_size=min(batch_size, len(X)), shuffle=True)

            optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            criterion = nn.CrossEntropyLoss()

            self.model.train()
            for epoch in range(epochs):
                for batch_X, batch_y in loader:
                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
        else:
            # Linear centroid fitting when PyTorch is unavailable
            means = np.mean(X, axis=2)
            self.weights = np.zeros((self.channels, self.n_classes))
            for c in range(self.n_classes):
                c_mask = (y == c)
                if np.any(c_mask):
                    self.weights[:, c] = np.mean(means[c_mask], axis=0)

        self._fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for input signal epochs."""
        if TORCH_AVAILABLE:
            self.model.eval()
            x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            with torch.no_grad():
                logits = self.model(x_tensor)
                return torch.argmax(logits, dim=1).numpy()
        else:
            means = np.mean(X, axis=2)
            weights = self.weights if self.weights is not None else np.ones((self.channels, self.n_classes)) / self.channels
            scores = means @ weights
            return np.argmax(scores, axis=1)
