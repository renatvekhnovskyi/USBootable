from pathlib import Path
import platform
import sys


def get_app_path():
    """Return the directory containing the application."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).resolve().parent


def get_diskspd_executable():
    """Return the architecture name used by DiskSpd."""
    arch = platform.machine().lower()

    if arch in ("amd64", "x86_64"):
        return "amd64"

    elif arch in ("arm64", "aarch64"):
        return "arm64"

    elif arch in ("x86", "i386", "i686"):
        return "x86"

    raise RuntimeError(f"Unsupported architecture: {arch}")


def get_diskspd_path():
    """Return the path to the correct DiskSpd executable."""
    system = get_diskspd_executable()

    diskspd_path = (
        get_app_path()
        / "tools"
        / f"diskspd_{system}.exe"
    )

    if not diskspd_path.exists():
        raise FileNotFoundError(
            f"DiskSpd executable not found: {diskspd_path}"
        )

    return diskspd_path