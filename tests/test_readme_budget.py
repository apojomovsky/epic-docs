import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import readme_budget

SKELETON = """# my-repo

A thing for hobbyists.

[![CI](x)](y) [![License: MIT](l)](LICENSE) [![Release](r)](t)

## Why my-repo

- **Fully open source, MIT licensed.** Reason here.
- Second reason.
- Third reason.

**Status:** Ready. See [What's in 1.0](hub/status/).

## The shortest example

```c
code
```

## Install

```bash
install
```

## Ways to use epic8

- CLI or PlatformIO.

## Where next

- Links.

## Contributing and licence

Text.
"""


class BudgetTest(unittest.TestCase):
    def test_conforming_readme_passes(self):
        self.assertEqual(readme_budget.check_readme(SKELETON), [])

    def test_long_readme_flagged(self):
        text = SKELETON + "\n".join(f"filler {i}" for i in range(200))
        warnings = readme_budget.check_readme(text)
        self.assertTrue(any("over the 120-line budget" in w for w in warnings))

    def test_boundary_is_120_lines(self):
        lines = SKELETON.splitlines()
        while len(lines) < 120:
            lines.append("filler")
        self.assertEqual(readme_budget.check_readme("\n".join(lines)), [])

    def test_missing_section_reported(self):
        text = SKELETON.replace("## Install\n", "")
        warnings = readme_budget.check_readme(text)
        self.assertTrue(any("Install" in w for w in warnings))

    def test_report_only_contract(self):
        self.assertEqual(readme_budget.main(["readme_budget.py",
                                             "/nonexistent-dir"]), 0)

    def test_unknown_option_exits_two(self):
        self.assertEqual(readme_budget.main(["readme_budget.py",
                                             "--nope"]), 2)


if __name__ == "__main__":
    unittest.main()
