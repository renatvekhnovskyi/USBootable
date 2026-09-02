from pathlib import Path


def build_diskspd_command(
    test: dict,
    diskspd: str | Path,
    drive: str,
    test_file: str = "test.dat",
) -> list[str]:
    """
    Build a DiskSpd command from a resolved test definition.

    The test dictionary should already contain defaults merged with
    test-specific settings.

    Parameters
    ----------
    test : dict
        Effective test configuration.
    diskspd : str | Path
        Path to the DiskSpd executable.
    drive : str
        Drive letter, e.g. "E:".
    test_file : str
        Name of the benchmark file.

    Returns
    -------
    list[str]
        DiskSpd command suitable for subprocess.run().
    """

    drive = drive.rstrip("\\/")
    diskspd = str(diskspd)

    cmd = [diskspd]

    # Duration
    cmd.append(f"-d{test['duration_seconds']}")

    # Threads
    cmd.append(f"-t{test['threads']}")

    # Queue depth
    cmd.append(f"-o{test['queue_depth']}")

    # Block size
    cmd.append(f"-b{test['block_size']}")

    # Test file size
    if "test_file_size" in test:
        cmd.append(f"-c{test['test_file_size']}")

    # Cache / buffering options
    if test.get("disable_cache", False):
        cmd.append("-Sh")

    elif test.get("disable_os_buffering", False):
        cmd.append("-Su")

    elif test.get("write_through", False):
        cmd.append("-Sw")

    # Access mode
    access = test["access"].lower()

    if access == "read":
        cmd.append("-w0")

    elif access == "write":
        cmd.append("-w100")

    elif access == "mixed":
        read_percentage = test.get("read_percentage", 50)

        if not 0 <= read_percentage <= 100:
            raise ValueError(
                "read_percentage must be between 0 and 100"
            )

        cmd.append(f"-w{100 - read_percentage}")

    else:
        raise ValueError(
            f"Unknown access mode: {access!r}"
        )

    # Access pattern
    if test.get("random", False):
        cmd.append("-r")

    # Target file
    target = f"{drive}\\USBootableBenchmark\\{test_file}"
    cmd.append(target)

    return cmd