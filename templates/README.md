# Page templates

Starting points for every page in the epic8 family. Pick the template that matches the page kind (see the [style guide](../docs/internals/style-guide.md)), copy it, replace every `{{...}}`, and delete the comments.

| Template | For |
|---|---|
| `README.md.tmpl` | Each repository's `README.src.md` (rendered to `README.md` by `make docs-gen`) |
| `tutorial.md.tmpl` | Getting started only |
| `how-to.md.tmpl` | Guides |
| `device-family.md.tmpl` | One reference page per device family |
| `hal-module.md.tmpl` | One reference page per HAL module |
| `example-README.md.tmpl` | Every example directory |

Shared includes live in `../includes/` and are pulled in with `--8<--`.
