#!/usr/bin/env python3
"""Nightly backstop for the vendored epic-docs copies (epic-docs#11).

Each consumer repository vendors includes/ways-to-use-epic8.md and records
the hub commit plus the copy sha256 in docs/snippets/SHARED-INCLUDES. That
record is self reported: editing the copy and recomputing its sha256 passes
the local check, and nothing ties the record to the hub file. This job
fetches the hub file at the recorded commit and compares it with the
consumer copy, so a hand rewritten record is caught within a day.

It runs on a schedule, never in the PR path, so PR checks stay offline and
the few fetches a day stay far under any rate limit. A fetch failure is a
failure: a silent skip would hide exactly the drift this job exists to
catch, and a rerun is one click under Actions.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import urllib.request

CONSUMERS = ("epic-cc", "epic-hal", "epic-platformio")

HUB = "apojomovsky/epic-docs"
HUB_FILE = "includes/ways-to-use-epic8.md"
COPY = "docs/snippets/ways-to-use-epic8.md"
RECORD = "docs/snippets/SHARED-INCLUDES"
RAW_URL = "https://raw.githubusercontent.com/{hub}/{commit}/{path}"

_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_record(text: str) -> dict[str, str]:
    """The `key = value` lines of a SHARED-INCLUDES record; `#` lines skipped."""
    fields = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ValueError(f"malformed line {line!r}, want key = value")
        fields[key.strip()] = value.strip()
    return fields


def fetch_hub(commit: str) -> bytes:
    url = RAW_URL.format(hub=HUB, commit=commit, path=HUB_FILE)
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read()


def verify_consumer(root: str, fetch=fetch_hub) -> list[str]:
    """Problems with one consumer's vendored copy; empty means it is clean."""
    record_path = os.path.join(root, RECORD)
    copy_path = os.path.join(root, COPY)
    if not os.path.isfile(record_path):
        return [f"{RECORD} missing; the repo vendors no hub copy to verify"]
    try:
        with open(record_path, encoding="utf-8") as handle:
            fields = parse_record(handle.read())
    except (OSError, ValueError) as exc:
        return [f"{RECORD}: {exc}"]
    commit = fields.get("commit", "")
    if not _COMMIT_RE.match(commit):
        return [f"{RECORD}: commit must be a full 40-character sha"]
    if fields.get("source") != f"{HUB}:{HUB_FILE}":
        return [f"{RECORD}: source must be {HUB}:{HUB_FILE}"]
    if not os.path.isfile(copy_path):
        return [f"{COPY} missing; restore it or drop the {RECORD} record"]
    try:
        with open(copy_path, "rb") as handle:
            copy_digest = sha256_hex(handle.read())
    except OSError as exc:
        return [f"{COPY}: {exc}"]
    try:
        hub_digest = sha256_hex(fetch(commit))
    except OSError as exc:
        return [f"could not fetch {HUB}:{HUB_FILE} at {commit}: {exc}"]
    if hub_digest != copy_digest:
        return [
            f"{COPY} does not match {HUB}:{HUB_FILE} at the recorded"
            f" commit {commit} (hub sha256 {hub_digest}, copy sha256"
            f" {copy_digest}): the record was rewritten by hand."
            f" Change the hub file and sync, or restore the copy."
        ]
    record_digest = fields.get("sha256", "")
    if not _DIGEST_RE.match(record_digest):
        return [f"{RECORD}: sha256 must be 64 lowercase hex digits"]
    if record_digest != copy_digest:
        return [
            f"{RECORD} sha256 {record_digest} does not match"
            f" the copy sha256 {copy_digest}"
        ]
    return []


def sibling_dir() -> str:
    """Directory holding this clone next to its siblings, as in the Makefile."""
    import subprocess

    common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    base = common.stdout.strip() or ".git"
    return os.path.abspath(os.path.join(base, "..", ".."))


def main(argv: list[str] | None = None) -> int:
    """Check every consumer; positional args override the checkout paths."""
    given = (argv or [])[1:]
    if given and len(given) != len(CONSUMERS):
        print(
            f"verify: want {len(CONSUMERS)} checkout paths"
            f" ({' '.join(CONSUMERS)}), got {len(given)}",
            file=sys.stderr,
        )
        return 2
    failures = 0
    for repo, override in zip(CONSUMERS, given or [None] * len(CONSUMERS)):
        root = override or os.path.join(sibling_dir(), repo)
        if not os.path.isdir(root):
            print(f"verify: {repo} checkout missing at {root}", file=sys.stderr)
            failures += 1
            continue
        problems = verify_consumer(root)
        for problem in problems:
            print(f"verify: {repo}: {problem}", file=sys.stderr)
        failures += len(problems)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
