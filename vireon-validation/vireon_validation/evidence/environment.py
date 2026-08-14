"""
Environment capture for reproducibility evidence.

Records the exact execution environment so that reproducibility failures
can be diagnosed (e.g., numpy version differences, OS platform, etc.).
"""

import platform
import sys
from typing import Dict, Any


def capture_environment() -> Dict[str, Any]:
    """
    Capture the current execution environment as a serializable dict.
    This is written to environment.json in every evidence bundle.
    """
    env = {
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "os_name": platform.system(),
        "os_release": platform.release(),
    }

    # Capture numpy version
    try:
        import numpy as np
        env["numpy_version"] = np.__version__
    except ImportError:
        env["numpy_version"] = "not_installed"

    # Capture pydantic version
    try:
        import pydantic
        env["pydantic_version"] = pydantic.__version__
    except ImportError:
        env["pydantic_version"] = "not_installed"

    return env
