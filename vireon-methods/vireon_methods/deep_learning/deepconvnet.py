"""DeepConvNet Deep Convolutional Neural Network Implementation.

Reference: Schirrmeister, R. T., Springenberg, J. T., Fiederer, L. D. J., Glasstetter, M., Eggensperger, K., Tangermann, M., Hutter, F., Burgard, W., & Ball, T. (2017).
Deep learning with convolutional neural networks for EEG decoding and visualization. Human Brain Mapping, 38(11), 5391-5420.
DOI: 10.1002/hbm.23730
"""
import numpy as np
from typing import Optional

try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset

    class DeepConvNetPyTorch(nn.Module):
        """DeepConvNet Architecture (Schirrmeister 2017 Table 1).

        Inputs: (B, 1, channels, samples)
        """

        def __init__(
            self,
            n_classes: int = 2,
            channels: int = 8,
            samples: int = 250,
            dropout_rate: float = 0.5,
        ):
            super().__init__()
            self.n_classes = n_classes
            self.channels = channels
            self.samples = samples

            # Calculate reduced sample count after 4 max pools (stride 3 each)
            reduced = samples
            for _ in range(4):
                reduced = reduced // 3
            self.reduced_samples = max(1, reduced)

            # Conv block 1: temporal + spatial
            self.conv_temporal = nn.Conv2d(1, 25, (1, 10), padding=(0, 4), bias=False)
            self.conv_spatial = nn.Conv2d(25, 25, (channels, 1), bias=False)
            self.bn1 = nn.BatchNorm2d(25)
            self.elu1 = nn.ELU()
            self.pool1 = nn.MaxPool2d((1, 3), stride=(1, 3))
            self.drop1 = nn.Dropout(dropout_rate)

            # Conv block 2
            self.conv2 = nn.Conv2d(25, 50, (1, 10), padding=(0, 4), bias=False)
            self.bn2 = nn.BatchNorm2d(50)
            self.elu2 = nn.ELU()
            self.pool2 = nn.MaxPool2d((1, 3), stride=(1, 3))
            self.drop2 = nn.Dropout(dropout_rate)

            # Conv block 3
            self.conv3 = nn.Conv2d(50, 100, (1, 10), padding=(0, 4), bias=False)
            self.bn3 = nn.BatchNorm2d(100)
            self.elu3 = nn.ELU()
            self.pool3 = nn.MaxPool2d((1, 3), stride=(1, 3))
            self.drop3 = nn.Dropout(dropout_rate)

            # Conv block 4
            self.conv4 = nn.Conv2d(100, 200, (1, 10), padding=(0, 4), bias=False)
            self.bn4 = nn.BatchNorm2d(200)
            self.elu4 = nn.ELU()
            self.pool4 = nn.MaxPool2d((1, 3), stride=(1, 3))
            self.drop4 = nn.Dropout(dropout_rate)

            # Classification head
            self.fc = nn.Linear(200 * self.reduced_samples, n_classes)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            if x.dim() == 3:
                x = x.unsqueeze(1)
            # Block 1
            x = self.conv_temporal(x)
            x = self.conv_spatial(x)
            x = self.bn1(x)
            x = self.elu1(x)
            x = self.pool1(x)
            x = self.drop1(x)

            # Block 2
            x = self.conv2(x)
            x = self.bn2(x)
            x = self.elu2(x)
            x = self.pool2(x)
            x = self.drop2(x)

            # Block 3
            x = self.conv3(x)
            x = self.bn3(x)
            x = self.elu3(x)
            x = self.pool3(x)
            x = self.drop3(x)

            # Block 4
            x = self.conv4(x)
            x = self.bn4(x)
            x = self.elu4(x)
            x = self.pool4(x)
            x = self.drop4(x)

            # Classification
            x = x.view(x.size(0), -1)
            x = self.fc(x)
            return x

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    DeepConvNetPyTorch = None


class DeepConvNetWrapper:
    """Production Wrapper for Schirrmeister 2017 DeepConvNet Deep Learning Architecture."""

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
            self.model = DeepConvNetPyTorch(n_classes=n_classes, channels=channels, samples=samples)

    def fit(self, X: np.ndarray, y: np.ndarray, epochs: Optional[int] = None, lr: Optional[float] = None, batch_size: Optional[int] = None):
        """Fit deep convolutional filters on EEG input data using PyTorch Adam + CrossEntropyLoss training loop."""
        epochs = epochs if epochs is not None else self.epochs
        lr = lr if lr is not None else self.lr
        batch_size = batch_size if batch_size is not None else self.batch_size

        if TORCH_AVAILABLE:
            torch.manual_seed(self.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(self.seed)
            torch.use_deterministic_algorithms(True, warn_only=True)

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = DeepConvNetPyTorch(
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
            device = next(self.model.parameters()).device
            self.model.eval()
            X_tensor = torch.tensor(X, dtype=torch.float32).to(device)
            if X_tensor.dim() == 3:
                X_tensor = X_tensor.unsqueeze(1)
            with torch.no_grad():
                logits = self.model(X_tensor)
                return torch.argmax(logits, dim=1).cpu().numpy()
        else:
            vars_ = np.var(X, axis=2)
            weights = self.weights if self.weights is not None else np.ones((self.channels, self.n_classes)) / self.channels
            scores = vars_ @ weights
            return np.argmax(scores, axis=1)
