from pathlib import Path
from shutil import rmtree
from subprocess import run

from config_loader import load_config, load_preset
from architecture import get_diskspd_path

from diskspd_builder import build_diskspd_command
from output_parser import  parse_diskspd_output
from score import print_score_breakdown




TEST_DIRECTORY = "USBootableBenchmark"
TEST_FILENAME = "test.dat"


def get_active_preset(config: dict) -> tuple[str, dict]:
    """
    Return the name and definition of the currently selected preset.
    """

    preset_name = load_preset()

    try:
        preset = config["presets"][preset_name]
    except KeyError:
        raise ValueError(
            f"Preset '{preset_name}' does not exist."
        )

    return preset_name, preset

def validate_drive(drive: str) -> Path:
    path = Path(drive)

    if not path.exists():
        raise ValueError(
            f"Drive or path does not exist: {drive}"
        )

    if not path.is_dir():
        raise ValueError(
            f"Target is not a directory/drive: {drive}"
        )

    return path

def benchmark_drive(drive: str):
    """
    Run every enabled benchmark from the currently selected preset.

    Parameters
    ----------
    drive : str
        Drive letter, e.g. "E:".

    Returns
    -------
    dict
        Benchmark results keyed by test ID.
    """

    config = load_config()
    preset_name, preset = get_active_preset(config)

    diskspd = get_diskspd_path()

    validate_drive(drive)

    if not diskspd.exists():
        raise FileNotFoundError(
            f"DiskSpd executable not found: {diskspd}"
        )

    drive = drive.rstrip("\\/")

    test_directory = Path(
        f"{drive}\\{TEST_DIRECTORY}"
    )
    test_file = test_directory / TEST_FILENAME

    # Preset-specific tests inherit the global defaults.
    defaults = config.get("defaults", {})

    results = {}

    print(f"Benchmarking {drive}")
    print(f"Preset: {preset['name']}")
    print("-" * 50)

    test_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        for test_definition in preset["tests"]:

            if not test_definition.get("enabled", True):
                continue

            # Test-specific values override defaults.
            test = {
                **defaults,
                **test_definition,
            }

            test_id = test["id"]
            test_name = test.get("name", test_id)

            print(f"Running {test_name}...")

            command = build_diskspd_command(
                test,
                diskspd,
                drive,
            )

            completed = run(
                command,
                capture_output=True,
                text=True,
            )

            if completed.returncode != 0:
                print("DiskSpd stdout:")
                print(completed.stdout)

                print("DiskSpd stderr:")
                print(completed.stderr)

                raise RuntimeError(
                    f"DiskSpd failed with exit code {completed.returncode}"
                )

            result = parse_diskspd_output(
                completed.stdout,
                test_id,
                test["access"],
            )

            results[test_id] = result

    finally:
        cleanup_test_data(
            test_file,
            test_directory,
        )

    print()
    print_score_breakdown(
        results,
        preset["scoring"],
    )

    return results


def cleanup_test_data(
    test_file: Path,
    test_directory: Path,
):
    """
    Remove DiskSpd test data after the benchmark.
    """

    try:
        if test_file.exists():
            test_file.unlink()

        if test_directory.exists():
            rmtree(test_directory)
            print(f"Cleaned up {test_directory}")

    except OSError as exc:
        print(
            f"Warning: could not clean up test data: {exc}"
        )


def _cleanup_test_data(
    test_file: Path,
    test_directory: Path,
):
    """
    Remove benchmark files and directories.
    """

    try:
        if test_file.exists():
            test_file.unlink()

        if test_directory.exists():
            rmtree(test_directory)
            print(f"Cleaned up {test_directory}")

    except OSError as exc:
        print(
            f"Warning: could not clean up test data: {exc}"
        )

def list_tests():
    config = load_config()
    preset_name = load_preset()

    preset = config["presets"][preset_name]

    print(f"Available tests ({preset['name']}):\n")

    for test in preset["tests"]:
        state = "Enabled" if test.get("enabled", True) else "Disabled"
        print(f"{test['id']} ({state})")



