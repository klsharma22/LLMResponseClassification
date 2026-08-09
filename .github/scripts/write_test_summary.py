import os
import xml.etree.ElementTree as ET

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

summary = (
    "## Test Results\n\n"
    "| Metric | Count |\n"
    "| --- | --- |\n"
    f"| Total | {total} |\n"
    f"| Passed | {passed} |\n"
    f"| Failed | {failures} |\n"
    f"| Errors | {errors} |\n"
    f"| Skipped | {skipped} |\n\n"
    f"**Pass rate: {pass_rate:.1f}%**\n"
)

with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
    f.write(summary)
