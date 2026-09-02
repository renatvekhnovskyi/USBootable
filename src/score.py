from __future__ import annotations

import math


def interpolate_score(
    value: float,
    curve: list[list[float]],
) -> float:
    """
    Convert a raw benchmark measurement into a score.

    The configured curve defines the reference score from 0 to 100.

    Above the final curve point, performance continues to increase
    the score using a logarithmic diminishing-return function.

    This means:
        - The final curve point always equals 100.
        - Faster hardware can score above 100.
        - Additional performance has progressively less impact.
    """

    if not curve:
        raise ValueError("Scoring curve cannot be empty.")

    if len(curve) == 1:
        x, y = map(float, curve[0])

        if value <= x:
            return y

        # No meaningful slope can be calculated from one point.
        # Use logarithmic growth based on the reference point.
        return 100.0 + 20.0 * math.log2(value / x)

    points = [
        (float(point[0]), float(point[1]))
        for point in curve
    ]

    points.sort(key=lambda point: point[0])

    # ---------------------------------------------------------
    # Below the first point
    # ---------------------------------------------------------

    if value <= points[0][0]:
        return points[0][1]

    # ---------------------------------------------------------
    # Between curve points
    # ---------------------------------------------------------

    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if x1 <= value <= x2:
            if x1 == x2:
                return y2

            ratio = (value - x1) / (x2 - x1)

            return y1 + ratio * (y2 - y1)

    # ---------------------------------------------------------
    # Above the final curve point
    #
    # Use logarithmic diminishing returns.
    # ---------------------------------------------------------

    reference_x, reference_score = points[-1]
    previous_x, previous_score = points[-2]

    if reference_x <= 0:
        raise ValueError(
            "Final curve measurement must be greater than zero."
        )

    if reference_score <= 0:
        raise ValueError(
            "Final curve score must be greater than zero."
        )

    if value <= reference_x:
        return reference_score

    # The final curve segment determines how aggressively
    # the score continues above 100.
    #
    # Example:
    #
    #   [1000, 75]
    #   [2000, 100]
    #
    # Final segment:
    #   25 points for doubling the performance.
    #
    # We use that relationship as the logarithmic growth rate.
    score_delta = reference_score - previous_score

    if score_delta <= 0:
        # Fallback for a malformed/non-increasing final segment.
        score_delta = 25.0

    # Performance ratio relative to the 100-point reference.
    ratio = value / reference_x

    # Every doubling adds score_delta points.
    #
    # log2(1) = 0
    # log2(2) = 1
    # log2(4) = 2
    # log2(8) = 3
    #
    # Therefore:
    #
    # 1x reference -> 100
    # 2x reference -> 100 + delta
    # 4x reference -> 100 + 2*delta
    # 8x reference -> 100 + 3*delta
    #
    extension = score_delta * math.log2(ratio)

    return reference_score + extension


def get_measurement(
    results: dict,
    test_id: str,
    test_scoring: dict,
) -> float:
    """
    Extract the metric configured for a test.
    """

    if test_id not in results:
        raise KeyError(
            f"Missing result for test '{test_id}'."
        )

    result = results[test_id]

    if not isinstance(result, dict):
        raise TypeError(
            f"Expected result for '{test_id}' to be a dictionary, "
            f"got {type(result).__name__}: {result!r}"
        )

    metric = test_scoring.get("metric")

    if not metric:
        raise ValueError(
            f"No metric configured for test '{test_id}'."
        )

    if metric not in result:
        raise KeyError(
            f"Metric '{metric}' not found in result for "
            f"test '{test_id}'. Available fields: "
            f"{list(result.keys())}"
        )

    return float(result[metric])


def calculate_score(
    results: dict,
    scoring: dict,
) -> float:
    """
    Calculate the weighted score for a preset.

    The final score is not capped at 100.
    """

    scoring_tests = scoring.get("tests", {})

    valid_tests = [
        test_id
        for test_id in scoring_tests
        if test_id in results
    ]

    if not valid_tests:
        raise ValueError(
            "No valid test results to score."
        )

    total_weight = sum(
        scoring_tests[test_id]["weight"]
        for test_id in valid_tests
    )

    if total_weight <= 0:
        raise ValueError(
            "Total scoring weight must be greater than zero."
        )

    score = 0.0

    for test_id in valid_tests:
        test_scoring = scoring_tests[test_id]

        measurement = get_measurement(
            results,
            test_id,
            test_scoring,
        )

        test_score = interpolate_score(
            measurement,
            test_scoring["curve"],
        )

        normalized_weight = (
            test_scoring["weight"] / total_weight
        )

        score += test_score * normalized_weight

    return score


def print_score_breakdown(
    results: dict,
    scoring: dict,
):
    """
    Print benchmark measurements, metric, individual score,
    weight, and weighted contribution.
    """

    scoring_tests = scoring.get("tests", {})

    valid_tests = [
        test_id
        for test_id in scoring_tests
        if test_id in results
    ]

    if not valid_tests:
        raise ValueError(
            "No valid test results to display."
        )

    total_weight = sum(
        scoring_tests[test_id]["weight"]
        for test_id in valid_tests
    )

    if total_weight <= 0:
        raise ValueError(
            "Total scoring weight must be greater than zero."
        )

    print()
    print("=" * 110)
    print("                                               USBOOTABLE SCORE")
    print("=" * 110)

    print(
        f"{'Test':<28}"
        f"{'Metric':<22}"
        f"{'Measurement':>16}"
        f"{'Test Score':>14}"
        f"{'Weight':>10}"
        f"{'Contribution':>16}"
    )

    print("-" * 110)

    score = 0.0

    for test_id in valid_tests:
        test_scoring = scoring_tests[test_id]

        metric = test_scoring["metric"]
        weight = test_scoring["weight"]

        measurement = get_measurement(
            results,
            test_id,
            test_scoring,
        )

        test_score = interpolate_score(
            measurement,
            test_scoring["curve"],
        )

        normalized_weight = weight / total_weight

        contribution = test_score * normalized_weight

        print(
            f"{test_id:<28}"
            f"{metric:<22}"
            f"{measurement:>16.2f}"
            f"{test_score:>14.2f}"
            f"{weight:>10.2f}"
            f"{contribution:>16.2f}"
        )

        score += contribution

    print("-" * 110)

    print(
        f"{'Final Score':<28}"
        f"{'':<22}"
        f"{'':>16}"
        f"{score:>14.1f}"
        f"{'':>10}"
        f"{'':>16}"
    )

    print("=" * 110)