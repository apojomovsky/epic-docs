"""The nightly backstop must catch a hand rewritten SHARED-INCLUDES record.

Each consumer vendors includes/ways-to-use-epic8.md from apojomovsky/epic-docs;
these tests run verify_consumer() against temporary checkouts, so no network
is touched: the hub fetch is injected.
"""

import hashlib
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import verify_shared_includes

COMMIT = "2ad7d851c1d39888dda84adcbf9fa8d0667453c8"
OTHER_COMMIT = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
HUB_TEXT = b"## Ways to use epic8\n\n- **Command line:** one line.\n"


def _write(root, rel, data):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(data, bytes) else "w"
    with open(path, mode) as handle:
        handle.write(data)


def _record(commit, digest):
    return (
        "# Vendored from apojomovsky/epic-docs.\n"
        f"source = apojomovsky/epic-docs:{verify_shared_includes.HUB_FILE}\n"
        f"commit = {commit}\n"
        f"sha256 = {digest}\n"
    )


def _synced_root(root, hub_text=HUB_TEXT, commit=COMMIT):
    digest = hashlib.sha256(hub_text).hexdigest()
    _write(root, verify_shared_includes.COPY, hub_text)
    _write(root, verify_shared_includes.RECORD, _record(commit, digest))
    return root


def _verify(root, hub_text=HUB_TEXT):
    return verify_shared_includes.verify_consumer(
        root, fetch=lambda commit: hub_text
    )


class VerifyConsumerTest(unittest.TestCase):
    def test_synced_copy_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(_verify(_synced_root(tmp)), [])

    def test_hand_recomputed_record_fails(self):
        # The gap from epic-docs#11: the copy is edited and the record
        # sha256 recomputed, so the local check passes. The fetched hub
        # bytes still expose it.
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp)
            edited = HUB_TEXT + b"edited here\n"
            _write(root, verify_shared_includes.COPY, edited)
            _write(
                root,
                verify_shared_includes.RECORD,
                _record(COMMIT, hashlib.sha256(edited).hexdigest()),
            )
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("rewritten by hand", problems[0])

    def test_record_pointing_at_other_commit_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp, commit=OTHER_COMMIT)
            problems = _verify(root, hub_text=b"other hub content\n")
            self.assertEqual(len(problems), 1)
            self.assertIn(OTHER_COMMIT, problems[0])

    def test_record_digest_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp)
            _write(
                root,
                verify_shared_includes.RECORD,
                _record(COMMIT, "0" * 64),
            )
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("does not match", problems[0])

    def test_malformed_record_digest_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp)
            _write(
                root,
                verify_shared_includes.RECORD,
                _record(COMMIT, "not-hex"),
            )
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("64 lowercase hex", problems[0])

    def test_missing_copy_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp)
            os.remove(os.path.join(root, verify_shared_includes.COPY))
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("missing", problems[0])

    def test_missing_record_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp)
            os.remove(os.path.join(root, verify_shared_includes.RECORD))
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn(verify_shared_includes.RECORD, problems[0])

    def test_short_commit_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = _synced_root(tmp, commit="2ad7d85")
            problems = _verify(root)
            self.assertEqual(len(problems), 1)
            self.assertIn("40-character", problems[0])

    def test_fetch_failure_fails(self):
        def _boom(commit):
            raise OSError("network down")

        with tempfile.TemporaryDirectory() as tmp:
            problems = verify_shared_includes.verify_consumer(
                _synced_root(tmp), fetch=_boom
            )
            self.assertEqual(len(problems), 1)
            self.assertIn("could not fetch", problems[0])


if __name__ == "__main__":
    unittest.main()
