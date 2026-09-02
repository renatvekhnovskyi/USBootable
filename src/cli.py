from typer import Typer, Argument, echo, Exit
from benchmark import benchmark_drive, list_tests
from config_loader import load_config, save_preset, load_preset

app = Typer(
    no_args_is_help=True,
    help="USBootable Drive Benchmark by illwerke vkw AG"
)


@app.command()
def benchmark(
    drive: str = Argument(
        ...,
        help="Drive to benchmark (e.g. E:)"
    )
):
    """
    Run all benchmarks configured by the current preset.
    """

    benchmark_drive(drive)


@app.command()
def tests():
    """
    Show benchmark tests in the current preset.
    """

    list_tests()


@app.command()
def preset(
    name: str | None = Argument(
        None,
        help="Preset to select."
    )
):
    """
    Show or change the active benchmark preset.
    """

    config = load_config()
    presets = config["presets"]

    if name is None:
        current = load_preset()

        echo(f"Current preset: {current}")
        echo("\nAvailable presets:")

        for preset_name in presets:
            marker = "*" if preset_name == current else " "
            echo(f" {marker} {preset_name}")

        return

    if name not in presets:
        echo(
            f"Unknown preset '{name}'. "
            f"Available presets: {', '.join(presets)}",
            err=True
        )
        raise Exit(code=1)

    save_preset(name)

    echo(f"Preset changed to '{name}'.")


@app.command()
def version():
    """
    Show program version.
    """

    print("USBootable Drive Benchmark v1.1")
    print("illwerke vkw AG")


if __name__ == "__main__":
    app()
