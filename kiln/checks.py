"""The checks of a run. Each reads the measurement report of the finished model
(kiln.measure.measure) and the target profile, and gives back one result:

    {"name": ..., "measured": ..., "limit": ..., "unit": ..., "passed": ...}

A check passes when measured <= limit. These two are placeholders until issue #11 settles
the full list; a new check is one more function in CHECKS.
"""
from kiln import KilnError


def _result(name, measured, limit, unit):
    return {"name": name, "measured": measured, "limit": limit, "unit": unit,
            "passed": measured <= limit}


def validator_errors(report, profile):
    """The Khronos glTF Validator finds no errors. Warnings, infos and hints are allowed."""
    verdict = report["validator"]
    if not verdict or not verdict["ran"]:
        raise KilnError("the Khronos glTF Validator did not run, so its check cannot be made"
                        + (f": {verdict['reason']}" if verdict else ""))
    return _result("validator_errors", verdict["errors"], 0, "errors")


def triangle_count(report, profile):
    """The model has no more triangles than the profile's triangle budget."""
    return _result("triangle_count", report["totals"]["triangles"],
                   profile["triangle_budget"], "triangles")


CHECKS = (validator_errors, triangle_count)


def run_checks(report, profile, checks=CHECKS):
    """Every check's result, in order. All are made, so one run reports every failure."""
    return [check(report, profile) for check in checks]


def describe(result):
    """One line for a person: the check, what was measured, the limit, and the overshoot."""
    line = (f"{result['name']}: measured {result['measured']:,} {result['unit']}, "
            f"limit {result['limit']:,}")
    if result["passed"]:
        return line + ", passed"
    over = result["measured"] - result["limit"]
    line += f", over by {over:,}"
    if result["limit"]:
        line += f" ({100 * over / result['limit']:.1f}%)"
    return line + ", FAILED"
