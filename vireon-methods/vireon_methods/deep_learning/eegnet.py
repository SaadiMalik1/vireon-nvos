"""EEGNet Deep Convolutional Neural Network Implementation.

Reference: Lawhern, V. J., Solon, A. J., Waytowich, N. R., Gordon, S. M., Hung, T. M., & Lance, B. J. (2018).
EEGNet: a compact convolutional neural network for EEG-based brain-computer interfaces. Journal of Neural Engineering, 15(5), 056013.
DOI: 10.1088/1741-2552/aace8c
"""
import numpy as np
from typing import Optional

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    class EEGNetPyTorch(nn.Module):
        """EEGNet-8,2 Architecture (Lawhern 2018 Figure 1).

        Inputs: (B, 1, channels, samples)
        """

        def __init__(
            self,
            n_classes: int = 2,
            channels: int = 8,
            samples: int = 250,
            f1: int = 8,
            d: int = 2,
            f2: int = 16,
            dropout_rate: float = 0.25,
            kernel_length: int = 64,
        ):
            super().__init__()
            self.n_classes = n_classes
            self.channels = channels
            self.samples = samples
            self.f1 = f1
            self.f2 = f2 if f2 is not None else f1 * d

            # Block 1: Temporal Conv + Depthwise Spatial Conv
            self.conv1 = nn.Conv2d(1, f1, (1, kernel_length), padding=(0, kernel_length // 2), bias=False)
            self.bn1 = nn.BatchNorm2d(f1)
            self.depthwise = nn.Conv2d(f1, f1 * d, (channels, 1), groups=f1, bias=False)
            self.bn2 = nn.BatchNorm2d(f1 * d)
            self.elu1 = nn.ELU()
            self.pool1 = nn.AvgPool2d((1, 4))
            self.drop1 = nn.Dropout(dropout_rate)

            # Block 2: Separable Conv (Depthwise + Pointwise)
            self.sep_conv = nn.Conv2d(f1 * d, f1 * d, (1, 16), padding=(0, 8), groups=f1 * d, bias=False)
            self.point_conv = nn.Conv2d(f1 * d, self.f2, (1, 1), bias=False)
            self.bn3 = nn.BatchNorm2d(self.f2)
            self.elu2 = nn.ELU()
            self.pool2 = nn.AvgPool2d((1, 8))
            self.drop2 = nn.Dropout(dropout_rate)

            # Flatten & Classification head
            # Downsampled samples by 4x then 8x -> T // 32
            reduced_samples = max(1, samples // 32)
            self.fc = nn.Linear(self.f2 * reduced_samples, n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            if x.dim() == 3:
                x = x.unsqueeze(1)
            # Block 1
            x = self.conv1(x)
            x = self.bn1(x)
            x = self.depthwise(x)
            x = self.bn2(x)
            x = self.elu1(x)
            x = self.pool1(x)
            x = self.drop1(x)

            # Block 2
            x = self.sep_conv(x)
            x = self.point_conv(x)
            x = self.bn3(x)
            x = self.elu2(x)
            x = self.pool2(x)
            x = self.drop2(x)

            # Classification
            x = x.view(x.size(0), -1)
            x = self.fc(x)
            return x

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    EEGNetPyTorch = None


class EEGNetWrapper:
    """Production Wrapper for Lawhern 2018 EEGNet Deep Learning Architecture."""

    def __init__(
        self,
        n_classes: int = 2,
        channels: int = 8,
        samples: int = 250,
        lr: float = 0.001,
        batch_size: int = 16,
        epochs: int = 50,
        seed: int = 42,
    ):
        self.n_classes = n_classes
        self.channels = channels
        self.samples = samples
        self.lr = lr
        self.batch_size = batch_size
        self.epochs = epochs
        self.seed = seed
        self.model = None
        self.weights = None
        self._fitted = False
        if TORCH_AVAILABLE:
            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
            self.model = EEGNetPyTorch(n_classes=n_classes, channels=channels, samples=samples)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: Optional[int] = None, lr: Optional[float] = None, batch_size: Optional[int] = None):
        """Fit spatial convolution weights on EEG epochs using PyTorch Adam + CrossEntropyLoss training loop."""
        epochs = epochs if epochs is not None else self.epochs
        lr = lr if lr is not None else self.lr
        batch_size = batch_size if batch_size is not None else self.batch_size

        if TORCH_AVAILABLE:
            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
            torch.use_deterministic_algorithms(True, warn_only=True)

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = EEGNetPyTorch(
                n_classes=self.n_classes,
                channels=self.channels,
                samples=self.samples,
            ).to(device)

            X_tensor = torch.tensor(X, dtype=torch.float32)
            if X_tensor.dim() == 3:
                X_tensor = X_tensor.unsqueeze(1)
            y_tensor = torch.tensor(y, dtype=torch.long)
            dataset = TensorDataset(X_tensor, y_tensor)

            g = torch.Generator()
            g.manual_seed(self.seed)
            loader = DataLoader(dataset, batch_size=min(batch_size, len(X)), shuffle=True, generator=g)

            optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
            criterion = nn.CrossEntropyLoss()

            self.model.train()
            for epoch in range(epochs):
                for batch_X, batch_y in loader:
                    batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                    optimizer.zero_grad()
                    outputs = self.model(batch_X)
                    loss = criterion(outputs, batch_y)
                    loss.backward()
                    optimizer.step()
        else:
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
            device = next(self.model.parameters()).device
            self.model.eval()
            X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
            if X_tensor.dim() == 3:
                X_tensor = X_tensor.unsqueeze(1)
            with torch.no_grad():
                logits = self.model(X_tensor)
                return torch.argmax(logits, dim=1).cpu().numpy()
        else:
            means = np.mean(X, axis=2)
            weights = self.weights if self.weights is not None else np.ones((self.channels, self.n_classes)) / self.channels
            scores = means @ weights
            return np.argmax(scores, axis=1)
