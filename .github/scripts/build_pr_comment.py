import json
import os
import xml.etree.ElementTree as ET

COMMENT_MARKER = "<!-- ci-test-report -->"


def read_test_results():
    tree = ET.parse("report.xml")
    root = tree.getroot()
    suites = root.findall("testsuite") if root.tag == "testsuites" else [root]

    total = failures = errors = skipped = 0
    for suite in suites:
        total += int(suite.get("tests", 0))
        failures += int(suite.get("failures", 0))
        errors += int(suite.get("errors", 0))
        skipped += int(suite.get("skipped", 0))

    passed = total - failures - errors - skipped
    pass_rate = (passed / total * 100) if total else 0.0
    return total, passed, failures, errors, skipped, pass_rate


def read_diff_coverage():
    if not os.path.exists("diff-coverage.json"):
        return None
    with open("diff-coverage.json") as f:
        return json.load(f)


def build_comment():
    total, passed, failures, errors, skipped, pass_rate = read_test_results()

    lines = [
        COMMENT_MARKER,
        "## CI Report",
        "",
        "### Test Results",
        "",
        "| Metric | Count |",
        "| --- | --- |",
        f"| Total | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {failures} |",
        f"| Errors | {errors} |",
        f"| Skipped | {skipped} |",
        "",
        f"**Pass rate: {pass_rate:.1f}%**",
        "",
    ]

    diff_data = read_diff_coverage()
    if diff_data is not None:
        total_lines = diff_data.get("total_num_lines", 0)
        violations = diff_data.get("total_num_violations", 0)
        covered_lines = total_lines - violations
        diff_pct = diff_data.get("total_percent_covered", 0)

        lines += [
            "### New/Changed Code Coverage",
            "",
            f"**{diff_pct:.1f}%** of the lines changed in this PR are covered by tests "
            f"({covered_lines}/{total_lines} new/changed lines).",
            "",
        ]

        src_stats = diff_data.get("src_stats", {})
        uncovered_files = {
            path: stats
            for path, stats in src_stats.items()
            if stats.get("percent_covered", 100) < 100
        }
        if uncovered_files:
            lines.append("Files with untested new/changed lines:")
            lines.append("")
            lines.append("| File | Coverage | Untested lines |")
            lines.append("| --- | --- | --- |")
            for path, stats in sorted(uncovered_files.items()):
                missing = ",".join(str(n) for n in stats.get("violation_lines", []))
                lines.append(f"| `{path}` | {stats['percent_covered']:.1f}% | {missing} |")
            lines.append("")
        else:
            lines.append("Every changed line in this PR is covered by a test. ✅")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    with open("pr_comment.md", "w") as f:
        f.write(build_comment())
