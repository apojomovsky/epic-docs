#!/usr/bin/env python3
"""README budget check (design docs/08-docs-overhaul.md section 5).

Reports, never fails: each project repository enforces its own README
(at most 120 lines, the section 5 skeleton). The hub only reports what
it sees so writers notice drift. Stdlib only; always exits 0, 2 on
usage error.
"""

import os
import re
import subprocess
import sys

REPOS = ("epic-cc", "epic-hal", "epic-platformio", "epic-tools")
BUDGET_LINES = 120

REQUIRED = [
    (re.compile(r"^#\s+\S+", re.MULTILINE), "name and one-sentence description"),
    (re.compile(r"\[\!\[.*?\]\(.*?\)\]"), "badges (CI, licence, release)"),
    (re.compile(r"^##\s+Why\b", re.MULTILINE | re.IGNORECASE), "'Why' section"),
    (re.compile(r"\*\*Status:\*\*|^##?\s+Status\b",
                re.MULTILINE), "status line"),
    (re.compile(r"shortest example", re.IGNORECASE),
     "'shortest example' section"),
    (re.compile(r"^##\s+Install\b", re.MULTILINE | re.IGNORECASE),
     "'Install' section"),
    (re.compile(r"Ways to use epic8", re.IGNORECASE), "ways-to-use include"),
    (re.compile(r"^##\s+Where next\b", re.MULTILINE | re.IGNORECASE),
     "'Where next' section"),
    (re.compile(r"^##\s+Contributing\b", re.MULTILINE | re.IGNORECASE),
     "'Contributing' section"),
]


def hub_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sibling_dir(root):
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-common-dir"], capture_output=True,
            text=True, cwd=root, check=True).stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return None
    if not os.path.isabs(out):
        out = os.path.abspath(os.path.join(root, out))
    return os.path.dirname(os.path.dirname(out))


def check_readme(text):
    """Warning strings for one README's text. Pure; used by tests."""
    warnings = []
    lines = text.splitlines()
    if len(lines) > BUDGET_LINES:
        warnings.append(f"{len(lines)} lines, over the {BUDGET_LINES}-line "
                        "budget")
    for pattern, label in REQUIRED:
        if not pattern.search(text):
            warnings.append(f"missing skeleton: {label}")
    return warnings


def main(argv):
    args = argv[1:]
    if "--help" in args:
        sys.stdout.write(__doc__ + "\nusage: readme_budget.py [DIR...]\n")
        return 0
    unknown = [a for a in args if a.startswith("-")]
    if unknown:
        sys.stderr.write(f"unknown option: {' '.join(unknown)}\n")
        return 2
    root = hub_root()
    sib = sibling_dir(root)
    dirs = args or ([os.path.join(sib, r) for r in REPOS]
                    if sib is not None else [])
    if not dirs:
        print("readme_budget: no sibling checkouts found; skipping")
        return 0
    for repo_dir in dirs:
        name = os.path.basename(os.path.normpath(repo_dir))
        readme = os.path.join(repo_dir, "README.md")
        try:
            with open(readme, encoding="utf-8") as handle:
                text = handle.read()
        except OSError:
            print(f"{name}: WARNING: no README.md to report on")
            continue
        warnings = check_readme(text)
        if warnings:
            for warning in warnings:
                print(f"{name}: WARNING: {warning}")
        else:
            print(f"{name}: OK "
                  f"({len(text.splitlines())} lines, skeleton complete)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
