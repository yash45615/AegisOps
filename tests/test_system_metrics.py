
import platform
from unittest.mock import Mock

import psutil

from aegisops.services import system_metrics


def test_get_system_metrics_returns_expected_fields(monkeypatch):
    memory = Mock()
    memory.total = 16_000_000_000
    memory.available = 8_000_000_000
    memory.percent = 50.0

    disk = Mock()
    disk.total = 500_000_000_000
    disk.used = 200_000_000_000
    disk.free = 300_000_000_000
    disk.percent = 40.0

    monkeypatch.setattr(psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(psutil, "disk_usage", lambda path: disk)
    monkeypatch.setattr(psutil, "cpu_percent", lambda interval: 25.0)
    monkeypatch.setattr(psutil, "cpu_count", lambda logical=True: 8)
    monkeypatch.setattr(system_metrics.platform, "system", lambda: "Windows")
    monkeypatch.setattr(system_metrics.platform, "release", lambda: "11")

    result = system_metrics.get_system_metrics()

    assert result["platform"] == "Windows"
    assert result["platform_release"] == "11"
    assert result["cpu_percent"] == 25.0
    assert result["cpu_count"] == 8
    assert result["memory"]["used_percent"] == 50.0
    assert result["disk"]["used_percent"] == 40.0
    assert result["disk"]["path"] == "C:\\"


def test_windows_disk_path():
    assert system_metrics._get_disk_path() == (
        "C:\\" if platform.system() == "Windows" else "/"
    )


def test_disk_path_for_linux(monkeypatch):
    monkeypatch.setattr(system_metrics.platform, "system", lambda: "Linux")

    assert system_metrics._get_disk_path() == "/"
