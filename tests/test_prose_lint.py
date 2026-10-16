import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import prose_lint


def findings(text, name="page.md"):
    return prose_lint.lint_lines(text.splitlines(), name)


class EmDashTest(unittest.TestCase):
    def test_clean_prose_passes(self):
        self.assertEqual(findings("You build the example with make.\n"), [])

    def test_em_dash_flagged(self):
        self.assertEqual(len(findings("It works \u2014 trust it.\n")), 1)

    def test_double_hyphen_allowed(self):
        self.assertEqual(findings("gh release download --pattern 'x*'\n"), [])


class TerminologyTest(unittest.TestCase):
    def test_epic8_variants(self):
        for bad in ("Epic8", "EPIC8", "epic 8-bit PICs"):
            self.assertEqual(len(findings(f"Use {bad} here.\n")), 1, bad)

    def test_repo_name_variants(self):
        self.assertEqual(len(findings("Build EpicCC first.\n")), 1)

    def test_midrange(self):
        self.assertEqual(len(findings("a midrange part\n")), 1)
        self.assertEqual(findings("a mid-range part\n"), [])

    def test_emulator(self):
        self.assertEqual(len(findings("run it in the emulator\n")), 1)

    def test_bare_hex(self):
        self.assertEqual(len(findings("flash the HEX file\n")), 1)
        self.assertEqual(findings("flash the hex file\n"), [])

    def test_code_spans_skipped(self):
        self.assertEqual(findings("run `make sim-epiccc HEX=x`\n"), [])

    def test_fenced_blocks_skipped(self):
        text = "```bash\nmake sim-epiccc HEX=x emulator=1\n```\n"
        self.assertEqual(findings(text), [])

    def test_style_guide_documents_variants(self):
        text = "| epic8 | Epic8, EPIC8 |\n"
        self.assertEqual(findings(text, "style-guide.md"), [])
    def test_intent_rows_left_to_reviewers(self):
        self.assertEqual(findings("flash the device\n"), [])
        self.assertEqual(findings("pick a target board\n"), [])



class BannedPhrasesTest(unittest.TestCase):
    def test_hype_words(self):
        self.assertEqual(len(findings("It simply works.\n")), 1)
        self.assertEqual(len(findings("Just run make.\n")), 1)

    def test_what_you_just_did_allowed(self):
        self.assertEqual(findings("## What you just did\n"), [])

    def test_xc8_with_number(self):
        found = findings("XC8 needs 100 bytes\n")
        self.assertEqual(len(found), 1)
        self.assertIn("next to a number", found[0][1])

    def test_xc8_comparison(self):
        for line in ("smaller than XC8\n", "no XC8 licence needed\n"):
            found = findings(line)
            self.assertEqual(len(found), 1, line)
            self.assertIn("comparison wording", found[0][1], line)

    def test_xc8_plain_mention_passes(self):
        self.assertEqual(findings("XC8 is free today.\n"), [])



class HeadingsTest(unittest.TestCase):
    def test_sentence_case_passes(self):
        self.assertEqual(findings("## Check that it works\n"), [])

    def test_title_case_flagged(self):
        self.assertEqual(len(findings("## Check That It Works\n")), 3)

    def test_first_word_always_allowed(self):
        self.assertEqual(findings("# Contributing\n"), [])

    def test_acronyms_and_parts_allowed(self):
        self.assertEqual(findings("# Send and receive over UART\n"), [])
        self.assertEqual(findings("## Part 1: in the simulator\n"), [])

    def test_slash_sections_allowed(self):
        self.assertEqual(findings("# Internals / Contributing\n"), [])


class VersionTest(unittest.TestCase):
    def test_bare_version_flagged(self):
        self.assertEqual(len(findings("supported in 2.0\n")), 1)

    def test_version_before_word_flagged(self):
        found = findings("supported in 1.0 today\n")
        self.assertEqual(len(found), 1)
        self.assertIn("version string", found[0][1])

    def test_measurements_allowed(self):
        self.assertEqual(findings("a 0.1 uF capacitor\n"), [])
        self.assertEqual(findings("runs at 3.3 V\n"), [])

    def test_spdx_identifiers_allowed(self):
        self.assertEqual(findings("The program is GPL-3.0-or-later.\n"), [])
        self.assertEqual(findings("| Licence | GPL-2.0-only |\n"), [])

    def test_status_page_variant_allowed(self):
        self.assertEqual(findings("see [What is in 1.0](status.md)\n"), [])

    def test_sentence_ending_version_flagged(self):
        found = findings("supported in 2.0.\n")
        self.assertEqual(len(found), 1)
        self.assertIn("version string", found[0][1])
    def test_status_page_link_allowed(self):
        self.assertEqual(findings("see [What's in 1.0](status.md)\n"), [])

    def test_code_skipped(self):
        self.assertEqual(findings("version = `2.0`\n"), [])

    def test_unclosed_fence_flagged(self):
        found = findings("Text.\n\n```c\nint x;\n")
        self.assertEqual(len(found), 1)
        self.assertIn("unclosed", found[0][1])

    def test_unknown_option_exits_two(self):
        self.assertEqual(prose_lint.main(["prose_lint.py", "--nope"]), 2)


if __name__ == "__main__":
    unittest.main()
