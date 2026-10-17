#!/usr/bin/env python3
"""Prose lint for the epic8 docs hub (design docs/08-docs-overhaul.md section 12).

Enforces the mechanically checkable style-guide rules over the hub-owned
markdown (docs/, projects/, README.md) and the sibling docs/user trees:
em-dash, terminology spellings, banned phrases (hype, XC8 comparisons),
sentence-case headings, version strings in prose. Intent-dependent rows
(device/part, series, driver/library, target/board, binary) stay with
human reviewers. Stdlib only; exit 1 on violation, 2 on usage error.
"""

import os
import re
import subprocess
import sys

HUB_OWNED_DIRS = ("docs", "projects")
HUB_OWNED_TOP = ("README.md",)
SIBLING_REPOS = ("epic-cc", "epic-hal", "epic-platformio", "epic-tools")
STYLE_GUIDE = "style-guide.md"
RULE_DOC_EXEMPT = (STYLE_GUIDE,)

EM_DASH = "\u2014"

TERMINOLOGY = [
    (re.compile(r"\bEpic8\b|\bEPIC8\b|\bepic 8\b"), "write 'epic8'"),
    (re.compile(r"\bEpicCC\b|\bepic_cc\b|\bEpic-HAL\b"),
     "write 'epic-cc' etc. exactly"),
    (re.compile(r"\bPIC16 core\b|\bmidrange\b|\benhanced-midrange\b",
                re.IGNORECASE), "write 'PIC14 (mid-range)' etc."),
    (re.compile(r"\bemulators?\b", re.IGNORECASE), "write 'simulator'"),
    (re.compile(r"\bHEX\b"), "write 'hex file'"),
]

HYPE_RE = re.compile(r"\b(blazing|powerful|simply|just|easy)\b", re.IGNORECASE)
JUST_DID = "What you just did"

XC8_COMPARISON_RES = [
    re.compile(r"\bno\s+xc8\b", re.IGNORECASE),
    re.compile(r"\bthan\s+xc8\b", re.IGNORECASE),
    re.compile(r"\bxc8\s+than\b", re.IGNORECASE),
    re.compile(r"\bcompar\w*\b.{0,30}\bxc8\b", re.IGNORECASE),
    re.compile(r"\bxc8\b.{0,30}\bcompar\w*\b", re.IGNORECASE),
    re.compile(r"\bversus\s+xc8\b|\bvs\.?\s*xc8\b|\bxc8\b.{0,10}\bvs\.?\b",
               re.IGNORECASE),
    re.compile(r"\bxc8\b.{0,20}\blicen[sc]e\b", re.IGNORECASE),
]
XC8_RE = re.compile(r"\bxc8\b", re.IGNORECASE)
DIGIT_RE = re.compile(r"\d")

VERSION_RUN_RE = re.compile(r"\bv?\d+(?:\.\d+)+\b")
WHATS_IN_RE = re.compile(r"What(?:'s| is) in 1\.0")
IDENT_CHAR_RE = re.compile(r"[A-Za-z0-9_\-]")
MEASURE_RE = re.compile(r"\A\s*(?:%|°C?|[VvAa]\b|ms\b|s\b|min\b"
                        r"|[pnµμum]?[Ff]\b|[MkG]?Hz\b|[kMGT]?B\b)")
# PICkit 3.5, PICkit 2 and MPLAB X name a Microchip product, not a
# release, so the version rule lets them through. Keep this list to
# names that actually appear in the tree; anything else stays a finding.
PRODUCT_NAME_RES = [
    re.compile(r"\bPICkit\s+2\b"),
    re.compile(r"\bPICkit\s+3\.5\b"),
    re.compile(r"\bMPLAB\s+X\b"),
]
PROPER_NOUNS = frozenset({
    "PlatformIO", "GitHub", "Linux", "Docker", "Arduino", "Microchip",
    "Mermaid", "Python", "Windows", "macOS", "Ubuntu", "Debian",
    "C",
})

FENCE_RE = re.compile(r"^(```|~~~)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")


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


def strip_prose(line):
    line = INLINE_CODE_RE.sub("", line)
    return LINK_RE.sub(r"\1", line)


def split_fences(lines):
    """Yield (line, in_fence) for each line."""
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line.strip()):
            in_fence = not in_fence
            yield line, True
        else:
            yield line, in_fence


def check_heading(text, lineno, path):
    words = re.sub(r"[*_]", "", text).split()
    findings = []
    for i, raw in enumerate(words[1:], start=1):
        word = raw.strip("()[]{}\"'!?;:,.")
        if not word or word[0].isdigit() or not word[0].isalpha():
            continue
        prev = words[i - 1].rstrip("()[]{}\"'!?;:,.")
        if prev.endswith("/"):
            continue
        if len(word) >= 2 and word.isupper():
            continue
        if any(ch.isdigit() for ch in word):
            continue
        if word in PROPER_NOUNS:
            continue
        if word[0].isupper():
            findings.append((lineno,
                             f"[{path}] heading not sentence case: '{word}'"))
    return findings


def check_version(prose, lineno, path):
    findings = []
    clean = WHATS_IN_RE.sub("", prose)
    products = [span for pattern in PRODUCT_NAME_RES
                for span in (match.span() for match in pattern.finditer(clean))]
    for match in VERSION_RUN_RE.finditer(clean):
        token = match.group(0)
        if any(start <= match.start() and match.end() <= end
               for start, end in products):
            continue
        if len(token.split(".")) > 3 or token.count(".") >= 3:
            continue
        before = clean[match.start() - 1] if match.start() > 0 else ""
        after = clean[match.end():match.end() + 1]
        if (before and IDENT_CHAR_RE.match(before)) or (
                after and IDENT_CHAR_RE.match(after)):
            continue
        if MEASURE_RE.match(clean[match.end():]):
            continue
        findings.append((lineno,
                         f"[{path}] version string in prose: '{token}'"))
    return findings


def lint_lines(lines, filename):
    """All findings for one file's lines. Pure; used by tests."""
    findings = []
    ruledoc = os.path.basename(filename) in RULE_DOC_EXEMPT
    fenced = list(split_fences(lines))
    if fenced and fenced[-1][1] and not FENCE_RE.match(fenced[-1][0].strip()):
        findings.append((len(lines), f"[{filename}] unclosed code block"))
    for lineno, (line, in_fence) in enumerate(fenced, start=1):
        if EM_DASH in line:
            findings.append((lineno, f"[{filename}] em-dash; use a colon, "
                             "a comma or a new sentence"))
        stripped = line.strip()
        if in_fence or not stripped.startswith("#"):
            if not in_fence and not stripped.startswith("#") and not ruledoc:
                prose = strip_prose(line)
                for pattern, fix in TERMINOLOGY:
                    if pattern.search(prose):
                        findings.append((lineno, f"[{filename}] terminology: "
                                         f"{fix}"))
                hype_line = prose.replace(JUST_DID, "")
                if HYPE_RE.search(hype_line):
                    findings.append((lineno, f"[{filename}] banned hype "
                                     "word; show it working instead"))
                if XC8_RE.search(prose):
                    rest = XC8_RE.sub("", prose)
                    if DIGIT_RE.search(rest):
                        findings.append((lineno, f"[{filename}] XC8 next to "
                                         "a number; numbers stay private"))
                    elif any(r.search(prose) for r in XC8_COMPARISON_RES):
                        findings.append((lineno, f"[{filename}] XC8 "
                                         "comparison wording"))
                findings.extend(check_version(prose, lineno, filename))
            continue
        match = HEADING_RE.match(stripped)
        if match:
            findings.extend(check_heading(match.group(2), lineno, filename))
    return findings


def collect_files(root, extra_dirs=()):
    found = []
    for rel in list(HUB_OWNED_DIRS) + list(extra_dirs):
        top = os.path.join(root, rel)
        for base, _, files in os.walk(top):
            found.extend(os.path.join(base, f) for f in sorted(files)
                         if f.endswith(".md"))
    for top_file in HUB_OWNED_TOP:
        path = os.path.join(root, top_file)
        if os.path.isfile(path):
            found.append(path)
    sib = sibling_dir(root)
    if sib is not None:
        for repo in SIBLING_REPOS:
            user = os.path.join(sib, repo, "docs", "user")
            if os.path.isdir(user):
                for base, _, files in os.walk(user):
                    found.extend(os.path.join(base, f) for f in sorted(files)
                                 if f.endswith(".md"))
    return sorted(found)


def main(argv):
    args = argv[1:]
    if "--help" in args:
        sys.stdout.write(__doc__ + "\nusage: prose_lint.py [PATH...]\n")
        return 0
    unknown = [a for a in args if a.startswith("-")]
    if unknown:
        sys.stderr.write(f"unknown option: {' '.join(unknown)}\n")
        return 2
    paths = args
    root = hub_root()
    if not paths:
        paths = collect_files(root)
    else:
        expanded = []
        for path in paths:
            if os.path.isdir(path):
                for base, _, files in os.walk(path):
                    expanded.extend(os.path.join(base, f)
                                    for f in sorted(files)
                                    if f.endswith(".md"))
            else:
                expanded.append(path)
        paths = sorted(expanded)
    failed = False
    for path in paths:
        try:
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
        except OSError as exc:
            print(f"{path}: cannot read: {exc}")
            failed = True
            continue
        for lineno, message in lint_lines(lines, path):
            print(f"{path}:{lineno}: {message}")
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
