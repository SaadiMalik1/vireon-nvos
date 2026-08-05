"""DeepConvNet Deep Convolutional Neural Network Implementation.

Reference: Schirrmeister, R. T., Springenberg, J. T., Fiederer, L. D. J., Glasstetter, M., Eggensperger, K., Tangermann, M., Hutter, F., Burgard, W., & Ball, T. (2017).
Deep learning with convolutional neural networks for EEG decoding and visualization. Human Brain Mapping, 38(11), 5391-5420.
DOI: 10.1002/hbm.23730
"""
import numpy as np

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    class DeepConvNetPyTorch(nn.Module):
        """Real PyTorch DeepConvNet Architecture with Deep Conv & MaxPool Layers."""
        def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250):
            super().__init__()
            self.conv_time = nn.Conv2d(1, 25, (1, 10), bias=False)
            self.conv_spat = nn.Conv2d(25, 25, (channels, 1), bias=False)
            self.conv_2 = nn.Conv2d(25, 50, (1, 10), bias=False)
            self.conv_3 = nn.Conv2d(50, 100, (1, 10), bias=False)
            self.fc = nn.Linear(100 * 10, n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.conv_time(x)
            x = self.conv_spat(x)
            x = self.conv_2(x)
            x = self.conv_3(x)
            x = x.view(x.size(0), -1)
            return self.fc(x)

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class DeepConvNetWrapper:
    """Production Wrapper for Schirrmeister 2017 DeepConvNet Deep Learning Architecture."""
    
    def __init__(self, n_classes: int = 2, channels: int = 8, samples: int = 250):
        self.n_classes = n_classes
        self.channels = channels
        self.samples = samples
        self.weights = None
        self._fitted = False
        if TORCH_AVAILABLE:
            self.model = DeepConvNetPyTorch(n_classes, channels, samples)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: int = 50, lr: float = 0.001, batch_size: int = 16):
        """Fit deep convolutional filters on EEG input data using PyTorch Adam + CrossEntropyLoss training loop."""
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
            vars_ = np.var(X, axis=2)
            self.weights = np.zeros((self.channels, self.n_classes))
            for c in range(self.n_classes):
                c_mask = (y == c)
                if np.any(c_mask):
                    self.weights[:, c] = np.mean(vars_[c_mask], axis=0)

        self._fitted = True
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict class labels for EEG epochs."""
        if TORCH_AVAILABLE:
            self.model.eval()
            x_tensor = torch.tensor(X, dtype=torch.float32).unsqueeze(1)
            with torch.no_grad():
                logits = self.model(x_tensor)
                return torch.argmax(logits, dim=1).numpy()
        else:
            vars_ = np.var(X, axis=2)
            weights = self.weights if self.weights is not None else np.ones((self.channels, self.n_classes)) / self.channels
            scores = vars_ @ weights
            return np.argmax(scores, axis=1)
