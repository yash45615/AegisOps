
import platform
from typing import Any

import psutil


def get_system_metrics() -> dict[str, Any]:
    """Collect basic system metrics from the current machine."""
    memory = psutil.virtual_memory()

    disk_path = _get_disk_path()
    disk = psutil.disk_usage(disk_path)

    return {
        "platform": platform.system(),
        "platform_release": platform.release(),
        "cpu_percent": psutil.cpu_percent(interval=0.2),
        "cpu_count": psutil.cpu_count(logical=True),
        "memory": {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "used_percent": memory.percent,
        },
        "disk": {
            "path": disk_path,
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "used_percent": disk.percent,
        },
    }


def _get_disk_path() -> str:
    """Choose a disk path that works on Windows and Unix-like systems."""
    if platform.system() == "Windows":
        return "C:\\"

    return "/"
