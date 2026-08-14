"""Multi-platform hardware acceleration detection for VIREON.

Automatically detects and uses the best available compute backend:
- NVIDIA CUDA (via PyTorch CUDA)
- AMD ROCm (via PyTorch ROCm / HIP)
- Apple Metal (via PyTorch MPS)
- CPU fallback (always available)

No user configuration needed. Just `pip install vireon-nvos[gpu]` and
VIREON automatically uses whatever accelerator is present.
"""
import logging
import platform
import subprocess
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_device() -> str:
    """Get the best available compute device string.
    
    Auto-detects in priority order:
    1. NVIDIA CUDA (if torch + CUDA available)
    2. AMD ROCm/HIP (if torch + ROCm available)
    3. Apple Metal MPS (if torch + MPS available, macOS only)
    4. CPU (always available)
    
    Returns:
        str: "cuda", "rocm", "mps", or "cpu"
    """
    try:
        import torch
        
        # NVIDIA CUDA / AMD ROCm
        if torch.cuda.is_available():
            if hasattr(torch.version, "hip") and torch.version.hip is not None:
                return "rocm"
            return "cuda"
        
        # Apple Metal (macOS only)
        if platform.system() == "Darwin":
            if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"
    except ImportError:
        logger.debug("PyTorch not installed — using CPU")
    except Exception as e:
        logger.debug(f"Hardware detection error: {e}")
    
    return "cpu"


def get_device_info() -> Dict[str, Any]:
    """Get detailed hardware information for evidence bundles.
    
    Returns dict with:
    - device: "cuda" | "rocm" | "mps" | "cpu"
    - gpu_name: Name of GPU (if applicable)
    - gpu_vendor: "nvidia" | "amd" | "apple" | None
    - compute_backend: "cuda" | "rocm" | "mps" | "cpu"
    - driver_version: CUDA/ROCm driver version (if available)
    - gpu_memory_gb: Total GPU memory (if available)
    """
    device = get_device()
    info: Dict[str, Any] = {
        "device": device,
        "gpu_name": None,
        "gpu_vendor": None,
        "compute_backend": device,
        "driver_version": None,
        "gpu_memory_gb": None,
    }
    
    if device == "cuda":
        try:
            import torch
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_vendor"] = "nvidia"
            info["driver_version"] = getattr(torch.version, "cuda", None)
            props = torch.cuda.get_device_properties(0)
            info["gpu_memory_gb"] = round(props.total_memory / 1e9, 2)
            info["gpu_count"] = torch.cuda.device_count()
        except Exception:
            pass
    elif device == "rocm":
        try:
            import torch
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_vendor"] = "amd"
            info["driver_version"] = getattr(torch.version, "hip", None)
            props = torch.cuda.get_device_properties(0)
            info["gpu_memory_gb"] = round(props.total_memory / 1e9, 2)
            info["gpu_count"] = torch.cuda.device_count()
        except Exception:
            pass
    elif device == "mps":
        info["gpu_name"] = "Apple Metal (MPS)"
        info["gpu_vendor"] = "apple"
        try:
            res = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, timeout=5
            )
            for line in res.stdout.split("\n"):
                if "VRAM" in line:
                    vram_str = line.split(":")[-1].strip()
                    if "GB" in vram_str:
                        info["gpu_memory_gb"] = float(vram_str.replace("GB", "").strip())
                    elif "MB" in vram_str:
                        info["gpu_memory_gb"] = round(float(vram_str.replace("MB", "").strip()) / 1024, 2)
        except Exception:
            pass
            
    return info


def get_torch_device():
    """Get torch.device object for best available backend."""
    device = get_device()
    try:
        import torch
        if device in ("cuda", "rocm"):
            return torch.device("cuda")
        elif device == "mps":
            return torch.device("mps")
        return torch.device("cpu")
    except ImportError:
        return None


def to_device(data: Any, device: Optional[Any] = None) -> Any:
    """Move numpy array or torch tensor to specified device."""
    if device is None:
        device = get_torch_device()
    if device is None:
        return data
    try:
        import numpy as np
        import torch
        if isinstance(data, torch.Tensor):
            return data.to(device)
        elif isinstance(data, np.ndarray):
            return torch.from_numpy(data).to(device)
    except Exception:
        pass
    return data


def is_gpu_available() -> bool:
    """Check if any GPU accelerator (CUDA, ROCm, MPS) is available."""
    return get_device() != "cpu"
