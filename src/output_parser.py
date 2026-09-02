from __future__ import annotations

import re
from typing import Any


_SECTION_RE = re.compile(
    r"^(Read IO|Write IO|Total IO)\s*$",
    re.IGNORECASE,
)

_TOTAL_RE = re.compile(
    r"^Total:\s*(.*)$",
    re.IGNORECASE,
)

_NUMBER_RE = re.compile(
    r"^-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$"
)


def _parse_float(value: str) -> float | None:
    value = value.strip()

    if not _NUMBER_RE.match(value):
        return None

    try:
        return float(value)
    except ValueError:
        return None


def parse_diskspd_output(
    output: str,
    test_id: str,
    access: str,
) -> dict[str, Any]:
    """
    Parse the requested DiskSpd IO section.

    Returns named benchmark metrics that can be referenced
    directly by the scoring configuration.

    Supported metrics:

        - iops
        - throughput_mib_s

    The scoring configuration can therefore use:

        "metric": "iops"

    or:

        "metric": "throughput_mib_s"
    """

    access = access.lower()

    target_section = {
        "read": "read",
        "write": "write",
        "mixed": "total",
    }.get(access)

    if target_section is None:
        raise ValueError(
            f"Unknown access type: {access!r}. "
            "Expected: read, write, or mixed."
        )

    current_section: str | None = None

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        # Detect IO section.
        section_match = _SECTION_RE.match(line)

        if section_match:
            section_name = section_match.group(1).lower()

            current_section = {
                "read io": "read",
                "write io": "write",
                "total io": "total",
            }[section_name]

            continue

        # Ignore Total lines from other sections.
        if current_section != target_section:
            continue

        total_match = _TOTAL_RE.match(line)

        if not total_match:
            continue

        values = [
            value.strip()
            for value in total_match.group(1).split("|")
        ]

        if len(values) < 4:
            raise ValueError(
                f"Invalid DiskSpd total line for test "
                f"{test_id!r}: {line}"
            )

        # DiskSpd total-line layout used by this application:
        #
        #   column_0 = ...
        #   column_1 = IOPS
        #   column_2 = MiB/s
        #   column_3 = ...
        #
        # Keep these as named metrics so the scoring configuration
        # does not need to know about column numbers.

        iops = _parse_float(values[1])
        throughput_mib_s = _parse_float(values[2])

        if iops is None:
            raise ValueError(
                f"Could not parse IOPS from DiskSpd output "
                f"for test {test_id!r}: {values[1]!r}"
            )

        if throughput_mib_s is None:
            raise ValueError(
                f"Could not parse MiB/s from DiskSpd output "
                f"for test {test_id!r}: {values[2]!r}"
            )

        result: dict[str, Any] = {
            "test_id": test_id,
            "access": access,
            "iops": iops,
            "throughput_mib_s": throughput_mib_s,
        }

        # Preserve the original numeric columns as well.
        for index, value in enumerate(values):
            parsed = _parse_float(value)

            if parsed is not None:
                result[f"column_{index}"] = parsed

        return result

    raise ValueError(
        f"Could not find {target_section!r} IO result "
        f"for test {test_id!r}."
    )
